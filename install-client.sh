#!/usr/bin/env bash
# This file is part of ddnsp, see <https://github.com/MestreLion/ddnsp>
# Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
# -----------------------------------------------------------------------------

slug=ddnsp-client
bin=${XDG_BIN_HOME:-$HOME/.local/bin}/${slug}
log=${XDG_CACHE_HOME:-$HOME/.cache}/${slug}.stderr.log

bin_rel=client/client.sh
url=https://raw.githubusercontent.com/MestreLion/ddnsp/main/${bin_rel}
myself=${0##*/}
here=$(dirname "$(readlink -f "$0")")

default_config=${XDG_CONFIG_HOME:-"$HOME"/.config}/${slug}.conf
config=$default_config
cron_opts=''
opts=()
verbose=1

# -----------------------------------------------------------------------------

exists()  { type "$1" >/dev/null 2>&1; }
green()   { tput setaf 2; tput bold; printf '%s' "$@"; tput sgr0; }
message() { if (($# && verbose)); then green '* ' "$@"; echo; fi; }
escape()  { printf '%q' "$@"; }
argerr()  { printf '%s: %s\n' "${0##*/}" "${1:-error}" >&2; usage 1; }
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

	Personal DDNS Client installer

	Performs the following steps:
	- Install needed dependency packages (require 'sudo' privileges)
	- Download or symlink executable to '${bin}'
	- Create the configuration file and invoke 'editor' to edit it.
	- Set a crontab task, logging errors to '${log}'

	Options:
	  -h|--help         - show this page.
	  -c|--config FILE  - use FILE for configuration instead of the default:
	                      ${default_config}

	Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
	License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
	USAGE
	exit 0
}

for arg in "$@"; do [[ "$arg" == "-h" || "$arg" == "--help" ]] && usage; done
while (($#)); do
	case "$1" in
	-c | --config) shift; config=${1:-};;
	--config=*) config=${1#*=};;
	-*) invalid "$1" ;;
	*) argerr "$1" ;;
	esac
	shift || break
done

if [[ "$config" != "$default_config" ]]; then
	opts+=(-c "$config")
	cron_opts=" -c $(escape "$(readlink -f "$config")")"
fi

cron_opts="@hourly $(escape "$bin")${cron_opts} 2>> $(escape "$log")"
cron_opts=${cron_opts//"$HOME"/'~'}

# -----------------------------------------------------------------------------

message "Installing Personal DDNS Client: ${slug}"

# Install dependencies
if ! exists curl; then
	sudo apt install -y curl
fi

# Create tree for executable, config and log file
tree=()
for file in "$bin" "$config" "$log"; do
	tree+=( "$(dirname "$file")" )
done
# shellcheck disable=SC2174
mkdir -p -m 700 -- "${tree[@]}"

# Create executable, sym-linking or downloading it
rm -f -- "$bin"
if [[ -r "${here}/${bin_rel}" ]]; then
	# Running installer from local git repo, symlink client
	target=$(realpath --relative-to "${bin%/*}" -- "${here}/${bin_rel}")
	ln -s "$target" -- "$bin"
else
	# Running standalone installer, download client from github
	wget -O "$bin" -- "$url"
	chmod +x -- "$bin"
fi

# Run once to create the default blank config, and invoke the editor
"$bin" "${opts[@]}" --setup >/dev/null
"${EDITOR:-editor}" -- "$config"

# Add task to crontab
if ! crontab -l 2>/dev/null | grep -Fxq "$cron_opts"; then
	( (exec 2>/dev/null; crontab -l || EDITOR='cat' crontab -e) &&
		echo "$cron_opts" ) |
	crontab -
fi

message "Done!"
