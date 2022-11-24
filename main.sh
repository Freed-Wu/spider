#!/usr/bin/env bash
names=(data/*-data.json)
names=("${names[@]%%-data.json}")
parallel './main.jq {}-*.json > {/}.json' ::: "${names[@]}"
