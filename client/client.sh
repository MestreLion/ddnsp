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
config=${XDG_CONFIG_HOME:-"$HOME"/.config}/ddnsp-client.conf

# Constants
cache=${XDG_CACHE_HOME:-"$HOME"/.cache}/ddnsp-client.lastip.txt
logfile=${XDG_CACHE_HOME:-"$HOME"/.cache}/ddnsp-client.log

# Defaults for config file
ip_provider='https://api.ipify.org'
server='https://ddns.example.com'
username=${USER:-${LOGUSER:-$(whoami)}}
password=''
hostname=${HOSTNAME:-$(hostname)}

# State
myname=${0##*/}
ip=
action=
response=

#------------------------------------------------------------------------------

escape()    { printf '%q' "$@"; }
read_ip()   { cat -- "$cache" 2>/dev/null || true; }
timestamp() { date --rfc-3339=seconds; }
write_log() (
	exec >> "$logfile"
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

argerr()  { printf '%s: %s\n' "$myname" "${1:-error}" >&2; usage 1; }
invalid() { argerr "invalid ${2:-option}: ${1:-}"; }
usage() {
	if [[ "${1:-}" ]]; then exec >&2; fi
	cat <<-USAGE
		Usage: $myname [options]
	USAGE
	if [[ "${1:-}" ]]; then
		cat <<-USAGE
			Try '$myname --help' for more information.
		USAGE
		exit 1
	fi
	cat <<-USAGE

	Personal DDNS Client

	Options:
	  -h|--help         - show this page.
	  -c|--config FILE  - use FILE for configuration instead of the default:
	                      ${config}

	Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
	License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
	USAGE
	exit 0
}

for arg in "$@"; do [[ "$arg" == "-h" || "$arg" == "--help" ]] && usage; done
while (($#)); do
	case "$1" in
	-f | --force) shift; force=1;;
	-c | --config) shift; config=${1:-};;
	--config=*) config=${1#*=};;
	-*) invalid "$1" ;;
	*) argerr "$1" ;;
	esac
	shift || break
done

#------------------------------------------------------------------------------

if ! [[ -r "$config" ]]; then
	cat >>"$config" <<-EOF
		# Personal DDNS client config file
		# See https://github.com/MestreLion/ddnsp

		ip_provider=$(escape "$ip_provider")
		server=$(escape "$server")
		username=$(escape "$username")
		password=$(escape "$password")
		hostname=$(escape "$hostname")
	EOF
	chmod 600 -- "$config"
fi

# shellcheck source=$HOME/.config/ddnsp-client.conf
source "$config"

headers=(
	--user "${username}:${password}"
	# -H "Authorization: Bearer ${password}"
	# -H 'Content-Type: application/json'
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
	response=$(safecurl "${headers[@]}" "${data[@]}" -- "$server" || echo "fail")
	code=${response%% *}
	new_ip=${response#* }
	if [[ -z "$ip" ]] && [[ "$code" == 'good' ]] && [[ "$new_ip" ]]; then
		echo "$new_ip" > "$cache"
	fi
fi

write_log "${action:-nochg}" "${ip:--}" "$response"
