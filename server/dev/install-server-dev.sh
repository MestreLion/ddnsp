#!/usr/bin/env bash
# This file is part of ddnsp, see <https://github.com/MestreLion/ddnsp>
# Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
# -----------------------------------------------------------------------------

slug=ddnsp-server
url=https://github.com/MestreLion/ddnsp
verbose=1

xdg_data=${XDG_DATA_HOME:-"$HOME"/.local/share}
myself=${0##*/}
here=$(dirname "$(readlink -f -- "$0")")
server_dir=$(realpath --no-symlinks -- "$here"/..)

bin=$server_dir/server.sh
service=$xdg_data/systemd/user/$slug-dev.service  # or $xdg_config, same tail
unit=${service##*/}

# -----------------------------------------------------------------------------

install_packages() {
	# Avoid marking installed packages as manual by only installing missing ones
	local pkg=
	local pkgs=()
	local ok
	for pkg in "$@"; do
		# shellcheck disable=SC1083
		ok=$(pkg-query --showformat=\${Version} --show "$pkg" 2>/dev/null || true)
		if [[ -z "$ok" ]]; then pkgs+=( "$pkg" ); fi
	done
	if (("${#pkgs[@]}")); then
		sudo apt install "${pkgs[@]}"
	fi
}

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

	Personal DDNS Development Server installer

	Performs the following steps:
	- Install needed dependency packages (may require 'sudo' privileges)
	- Install and activate UFW Firewall rules
	- Install and start systemd unit daemon

	Options:
	  -h|--help         - show this page.

	Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
	License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
	USAGE
	exit 0
}

for arg in "$@"; do [[ "$arg" == "-h" || "$arg" == "--help" ]] && usage; done
# -----------------------------------------------------------------------------

message "Installing Personal DDNS Development Server: ${slug}"

# Install dependencies
install_packages git

# Create development config files from templates
# .env
config="$here"/../.env
if ! [[ -f "$config" ]]; then
	cp -- "$here"/env.template "$config"
fi
# instance/ddnsp.cfg
instance="$here"/../instance
config="$instance"/ddnsp.cfg
if ! [[ -f "$config" ]]; then
	mkdir -p -- "$instance"
	cp -- "$here"/ddnsp.cfg.template "$config"
fi

# source configs
configs=(
	"$here"/../.flaskenv
	"$here"/../.env
)
for config in "${configs[@]}"; do
	# shellcheck source=server/.flaskenv
	if [[ -r "$config" ]]; then source "$config"; fi
done
port=${FLASK_RUN_PORT:-5000}

# Install and activate UFW firewall rules
sudo tee /etc/ufw/applications.d/$slug <<-EOF
	# Personal DDNS Server
	# ${url}
	[DDNSP Server]
	title=Personal DDNS Server
	description=Personal Dynamic DNS Server
	ports=${port}/tcp
EOF
sudo ufw allow 'DDNSP Server'
sudo ufw reload

# Systemd user service unit
# https://wiki.archlinux.org/title/Systemd/User
# shellcheck disable=SC2174
mkdir -m 700 -p -- "$xdg_data"
mkdir        -p -- "$(dirname "$service")"
cat > "$service" <<-EOF
	[Unit]
	Description=Personal DDNS Development Server
	After=network.target

	[Service]
	ExecStart=$(escape "$bin")
	Restart=on-failure
	RestartSec=5

	[Install]
	WantedBy=default.target
EOF
systemctl --user daemon-reload
systemctl --user enable  "$unit"
systemctl --user restart "$unit"
#sudo loginctl enable-linger "$USER"  # optional

# Update Certbot keys / add deploy hook
# ...

message "Done!"
