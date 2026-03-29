util__cat_err() {
  cat "$@" >&2
}

util__echo_err() {
  IFS=" " echo "$*" >&2
}
