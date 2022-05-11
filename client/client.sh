#!/usr/bin/env bash
#
# client.sh - Personal DDNS Client
# https://github.com/MestreLion/ddnsp
#
# Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
# -----------------------------------------------------------------------------

set -Eeuo pipefail  # exit on any error
trap '>&2 echo "error: line $LINENO, status $?: $BASH_COMMAND"' ERR

#------------------------------------------------------------------------------

# Modifiable via CLI
force=0
setup=0
config=${XDG_CONFIG_HOME:-"$HOME"/.config}/ddnsp-client.conf

# Constants
myself=${0##*/}
cache=${XDG_CACHE_HOME:-"$HOME"/.cache}/ddnsp-client.lastip.txt
logfile=${XDG_CACHE_HOME:-"$HOME"/.cache}/ddnsp-client.log

# Defaults for config file
ip_provider='https://api.ipify.org'
server_url='https://dyndns.example.com:1234/update'
username=${USER:-${LOGUSER:-$(whoami)}}
password=PASSWORD
hostname=${HOSTNAME:-$(hostname)}

# State
ip=
action=
response=

#------------------------------------------------------------------------------

escape()    { printf '%q' "$@"; }
read_ip()   { cat -- "$cache" 2>/dev/null || true; }
timestamp() { date --rfc-3339=seconds; }
exists()    { type "$@" >/dev/null 2>&1; }
require()   {
	local cmd=$1
	local pkg=${2:-$cmd}
	local msg='' eol=''
	if exists "$cmd"; then return; fi
	if [[ -x /usr/lib/command-not-found ]]; then
		/usr/lib/command-not-found -- "$cmd" || true
		eol='\n'
	else
		echo "Required command '${cmd}' is not installed." >&2
		if [[ "$pkg" != '-' ]]; then
			msg="with:\n\tsudo apt install ${pkg}\n"
		fi
	fi
	echo -e "Please install ${cmd} ${msg}and try again.${eol}" >&2
	exit 1
}

write_log() (
	if [[ "${logfile:-}" ]]; then
		mkdir -p -- "$(dirname "$logfile")"
		exec >> "$logfile"
	fi
	local action=${1:-nochange}
	local ip=${2:--}
	local response=${3:-}
	printf '%s\t%s\t%s' "$(timestamp)" "$action" "$ip"
	if [[ "$response" ]]; then printf '\t%s' "$response"; fi
	printf '\n'
)
safecurl()  {
	local opts=(
		--silent           # -s, Don't show progress meter or error messages
		--show-error       # -S, With -s show an error message if it fails
		--get              # -G, Put the post data in the URL and use GET
		--location-trusted # follow redirects (-L) and re-send auth
		--max-time 30
		--connect-timeout 10
	)
	curl "${opts[@]}" "$@"
}

#------------------------------------------------------------------------------

argerr()  { printf '%s: %s\n' "$myself" "${1:-error}" >&2; usage 1; }
invalid() { argerr "invalid ${2:-option}: ${1:-}"; }
usage() {
	if [[ "${1:-}" ]]; then exec >&2; fi
	cat <<-USAGE
		Usage: $myself [options]
	USAGE
	if [[ "${1:-}" ]]; then
		cat <<-USAGE
			Try '$myself --help' for more information.
		USAGE
		exit 1
	fi
	cat <<-USAGE

	Personal DDNS Client

	Options:
	  -h|--help         - Show this page.
	  -f|--force        - Force IP update even if it did not change since last run.
	  -S|--setup        - Create the config file if missing, print its path, and exit.
	  -c|--config FILE  - Use FILE for configuration instead of the default location
	                          ${config}
	  -L|--no-log       - Output to stdout instead of the default log file at
	                          ${logfile}

	Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
	License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
	USAGE
	exit 0
}

for arg in "$@"; do [[ "$arg" == "-h" || "$arg" == "--help" ]] && usage; done
while (($#)); do
	case "$1" in
	-f | --force) force=1;;
	-S | --setup) setup=1;;
	-L | --no-log) logfile="";;
	-c | --config) shift; config=${1:-};;
	--config=*) config=${1#*=};;
	-*) invalid "$1" ;;
	*) argerr "$1" ;;
	esac
	shift || break
done

#------------------------------------------------------------------------------

if ! [[ -r "$config" ]]; then
	# shellcheck disable=SC2174
	mkdir -p -m 700 -- "$(dirname "$config")"
	cat >>"$config" <<-EOF
		# Personal DDNS client config file
		# See https://github.com/MestreLion/ddnsp

		ip_provider=$(escape "$ip_provider")
		server_url=$(escape "$server_url")
		username=$(escape "$username")
		password=$(escape "$password")
		hostname=$(escape "$hostname")
	EOF
	chmod 600 -- "$config"
	echo "A blank configuration file was created, please edit it and try again" >&2
	setup=1
fi
if ((setup)); then
	echo "$config"
	exit
fi

#------------------------------------------------------------------------------

require curl

# shellcheck source=$HOME/.config/ddnsp-client.conf
source "$config"

headers=(
	--user "${username}:${password}"
)
data=(--data-urlencode "hostname=$hostname")

if [[ "$ip_provider" ]]; then
	ip=$(safecurl -4 "$ip_provider" || echo)
fi
if [[ "$ip" ]]; then
	data+=(--data-urlencode "myip=$ip")
fi

if [[ -z "$ip" ]] || [[ "$ip" != "$(read_ip)" ]]; then
	action=update
	echo "$ip" > "$cache"
elif ((force)); then
	action=forced
else
	action=
fi

if [[ "$action" ]]; then
	response=$(safecurl "${headers[@]}" "${data[@]}" -- "$server_url" || echo fail)
	code=${response%% *}
	new_ip=${response#* }
	if [[ -z "$ip" ]] && [[ "$code" == 'good' ]] && [[ "$new_ip" ]]; then
		echo "$new_ip" > "$cache"
	fi
fi

write_log "${action:-nochg}" "${ip:--}" "$response"
