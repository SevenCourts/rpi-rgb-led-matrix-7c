# shellcheck source=./utils.bash
source "$(realpath "$(dirname "${BASH_SOURCE[0]}")/utils.bash")"

# Creates directory tree on WebDav server, like `mkdir -p ...` on Linux.
#
# Env:
#
# - WEBDAV_PASSWORD
# - WEBDAV_USERNAME
#
# Arguments:
#
# 1. The server, e.g. 'https://dl.sevencourts.com/remote.php/webdav'.
# 2. The directory tree to create on the server, e.g. 'sevencourts/apk'.
#
# Return code:
#
# - 0 on success.
# - 1 on error.
#
# STDERR:
#
# - errors.
# - logging.
webdav__mkdirp() {
  local tmp_file
  tmp_file="$(mktemp)"
  readonly tmp_file

  local server
  server="$1"
  readonly server

  local path
  path="$2"
  readonly path

  local username
  username="${WEBDAV_USERNAME:?}"
  readonly username

  local password
  password="${WEBDAV_PASSWORD:?}"
  readonly password

  util__echo_err 'Creating path'
  util__echo_err "  '$path'"
  util__echo_err "  on server '$server'"

  local -a path_segments
  mapfile -d '/' path_segments < <(echo "$path")
  readonly path_segments

  local http_code path_to_create
  for path_segment in "${path_segments[@]}"; do
    path_segment="$(echo "$path_segment" | tr -d '/' )"
    path_to_create+="/$path_segment"

    http_code="$(
      curl \
        --output "$tmp_file" \
        --request MKCOL \
        --silent \
        --user "$username:$password" \
        --write-out "%{http_code}" \
        "$server/$path_to_create"
    )"

    if (( http_code >= 400 )) && (( http_code != 405 )); then
      break
    fi
  done
  unset path_to_create
  readonly http_code

  if (( http_code == 201 )); then
    util__echo_err "  Created."
  elif (( http_code == 405 )); then
    util__echo_err "  Already exists."
  else
    util__echo_err "  Error, HTTP code $http_code."
    util__echo_err '  <=== Server Response ^ ===>'
    util__cat_err "$tmp_file"
    util__echo_err '  <=== Server Response $ ===>'
    return 1
  fi
}

# Checks if the path exists on the WebDav server.
#
# Env:
#
# - WEBDAV_PASSWORD
# - WEBDAV_USERNAME
#
# Arguments:
#
# 1. The server, e.g. 'https://dl.sevencourts.com/remote.php/webdav'.
# 2. The path to check for existence, e.g. 'sevencourts/apk' or 'build.info'.
#
# Return code:
#
# - 0 on success.
# - 1 on error.
#
# STDOUT:
#
# - exists -- if path exists.
# - not-exists -- if path not exists.
#
# STDERR:
#
# - errors.
# - logging.
webdav__path_exists() {
  local tmp_file
  tmp_file="$(mktemp)"
  readonly tmp_file

  local server
  server="$1"
  readonly server

  local path
  path="$2"
  readonly path

  local username
  username="${WEBDAV_USERNAME:?}"
  readonly username

  local password
  password="${WEBDAV_PASSWORD:?}"
  readonly password

  util__echo_err "Checking path exists"
  util__echo_err "  '$path'"
  util__echo_err "  on server '$server'"

  local http_code
  http_code="$(
    curl \
      --head \
      --output "$tmp_file" \
      --silent \
      --user "$username:$password" \
      --write-out "%{http_code}" \
      "$server/$path"
  )"
  readonly http_code

  if (( http_code == 200 )); then
    util__echo_err "  Exists."
    echo exists
  elif (( http_code == 404 )); then
    util__echo_err "  Not exists."
    echo not-exists
  else
    util__echo_err "  Error, HTTP code $http_code."
    util__echo_err '  <=== Server Response ^ ===>'
    util__cat_err "$tmp_file"
    util__echo_err '  <=== Server Response $ ===>'
    return 1
  fi
}

# Uploads the file to the WebDav server.
#
# Env:
#
# - WEBDAV_PASSWORD
# - WEBDAV_USERNAME
#
# Arguments:
#
# 1. The server, e.g. 'https://dl.sevencourts.com/remote.php/webdav'.
# 2. The directory on the server to upload the file to, e.g. 'sevencourts/apk'.
# 3. The file to upload, e.g. '/tmp/build.info'.
#
# Returns:
#
# - 0 on success.
# - 1 on error, e.g. the file already exists on the server.
#
# STDERR:
#
# - errors.
# - logging.
webdav__upload_file() {
  local tmp_file
  tmp_file="$(mktemp)"
  readonly tmp_file

  local server
  server="$1"
  readonly server

  local path
  path="$2"
  readonly path

  local file
  file="$3"
  readonly file

  local username
  username="${WEBDAV_USERNAME:?}"
  readonly username

  local password
  password="${WEBDAV_PASSWORD:?}"
  readonly password

  local file_name
  file_name="$(basename "$file")"
  readonly file_name

  util__echo_err 'Uploading file'
  util__echo_err "  '$file'"
  util__echo_err "  to server '$server'"
  util__echo_err "  to directory '$path'"
  util__echo_err "  as '$file_name'"

  if [[ ! -f $file ]]; then
    util__echo_err '  Error, the file to upload not exists or is not a file.'
    return 1
  fi

  local upload_url
  upload_url="$(
    realpath \
      --canonicalize-missing \
      --relative-to . \
      "$path/$file_name"
  )"
  readonly upload_url

  local path_exists
  path_exists="$(webdav__path_exists "$server" "$upload_url")"
  readonly path_exists

  if [[ $path_exists == exists ]]; then
    util__echo_err '  Error, file already exists.'
    return 1
  fi

  webdav__mkdirp "$server" "$path"

  local http_code
  http_code="$(
    curl \
      --output "$tmp_file" \
      --upload-file "$file" \
      --user "$username:$password" \
      --write-out "%{http_code}" \
      "$server/$path/"
   )"
  readonly http_code

  if (( http_code == 201 )); then
    util__echo_err '  Uploaded.'
  else
    util__echo_err "  Error, HTTP code $http_code"
    util__echo_err '  <=== Server Response ^ ===>'
    util__cat_err "$tmp_file"
    util__echo_err '  <=== Server Response $ ===>'
    return 1
  fi
}

# Uploads a file tree to the WebDav server.
#
# Arguments:
#
# 1. The server, e.g. 'https://dl.sevencourts.com/remote.php/webdav'.
# 2. The directory on the server to upload the file tree to, e.g. 'sevencourts/apk/master'.
# 3. The file tree to upload, e.g. '/tmp/apk'.
#
# Returns:
#
# - 0 on success.
# - 1 on error, e.g. the file already exists on the server.
#
# STDERR:
#
# - errors.
# - logging.
webdav__upload_directory() {
  local server
  server="$1"
  readonly server

  local base_path
  base_path="$2"
  readonly base_path

  local dir_to_upload
  dir_to_upload="$3"
  readonly dir_to_upload

  util__echo_err 'Uploading directory'
  util__echo_err "  '$dir_to_upload'"
  util__echo_err "  to server '$server'"
  util__echo_err "  to directory '$base_path'"
  util__echo_err

  if ! [[ -d $dir_to_upload ]]; then
    util__echo_err \
      "  Error, the directory to upload not exists or is not a directory: $dir_to_upload"
    return 1
  fi

  local -a files
  readarray -t files <<<"$(find "$dir_to_upload" -type f)"
  readonly files

  local file
  local path
  for file in "${files[@]}"; do
    path="$(
      realpath \
        --relative-to "$dir_to_upload" \
        "$(dirname "$file")"
    )"
    if [[ $path == . ]]; then
      path="$base_path"
    else
      path="$base_path/$path"
    fi

    webdav__upload_file "$server" "$path" "$file"
    util__echo_err
  done
}
