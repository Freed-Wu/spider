#!/usr/bin/env -S jq -srf
[(.[0] | keys[]) as $k | reduce .[] as $item (null; . += $item[$k])] |
unique_by(.id) | [.[] | {gender, school: .education.school, ip_location,
location, birthday, created_at, name, description, id}]
