#!/usr/bin/env bash
# This file is part of ddnsp - Personal self-hosting dynamic DNS
# See <https://github.com/MestreLion/ddnsp>
# Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later, at your choice. See <http://www.gnu.org/licenses/gpl>
# -----------------------------------------------------------------------------

slug=ddnsp-client
bin=${XDG_BIN_HOME:-$HOME/.local/bin}/${slug}
log=${XDG_CACHE_HOME:-$HOME/.cache}/${slug}.stderr.log
cron_line="@hourly ${bin/$HOME/'~'} 2>> ${log/$HOME/'~'}"

bin_rel=client/client.sh
url=https://raw.githubusercontent.com/MestreLion/ddnsp/main/${bin_rel}
here=$(dirname "$(readlink -f "$0")")

# -----------------------------------------------------------------------------

rm -f -- "$bin"
if [[ -r "${here}/${bin_rel}" ]]; then
	target=$(realpath --relative-to "${bin%/*}" -- "${here}/${bin_rel}")
	ln -s "$target" -- "$bin"
else
	wget -O "$bin" -- "$url"
	chmod +x -- "$bin"
fi

( (crontab -l || EDITOR='cat' crontab -e) && echo "$cron_line" ) | crontab -