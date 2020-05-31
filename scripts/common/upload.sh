#!/usr/bin/env bash
# shellcheck disable=SC1117

# Check dependencies.
set -e
[[ -n "${TRACE}" ]] && set -x

BRed='\033[31m'         # Red
BGreen='\033[32m'       # Green
NC="\033[0m"            # Color Reset

_OWNER=""
_REPO=""
_TAG=""
_FILENAME=""
_GITHUB_API_TOKEN=""
_ID=""

main() {

  # Define variables.
  GH_API="https://api.github.com"
  GH_REPO="$GH_API/repos/${_OWNER}/${_REPO}"
  AUTH="Authorization: token ${_GITHUB_API_TOKEN}"

  # Validate token.
  curl -o /dev/null -sH "$AUTH" "${GH_REPO}" || { echo "Error: Invalid repo, token or network issue!";  exit 1; }

  # Delete Existing Release
  GH_ASSET="https://api.github.com/repos/${_OWNER}/${_REPO}/releases"
  EXISTING_RELEASES="$(curl -s -H "Authorization: token ${_GITHUB_API_TOKEN}" "${GH_ASSET}")"

  if jq -e .[].id <<< "${EXISTING_RELEASES}" > /dev/null; then
    for release in $(jq .[].id <<< "${EXISTING_RELEASES}"); do
      curl -X DELETE -s -H "Authorization: token ${_GITHUB_API_TOKEN}" "${GH_ASSET}/${release}" > /dev/null
      echo -e "${BGreen}Deleted Release:${NC} ${BRed}${release}${NC}"
    done
  fi


  # Retag the master branch on latest commit local and remotes
  set +e
  if git push origin :refs/tags/${_TAG} 2>/dev/null; then
    git tag -d ${_TAG} 2>/dev/null
    git tag ${_TAG} 2>/dev/null
    git push origin --tags 2>/dev/null
  fi


  set -e

  # Create New Release, and Fetch it's ID
  _ID=$(curl -s -X POST -H "Authorization: token ${_GITHUB_API_TOKEN}" --data "{ \"tag_name\": \"${_TAG}\" }" "https://api.github.com/repos/${_OWNER}/${_REPO}/releases" | jq -r .id)
  echo -e "${BGreen}Created Release:${NC} ${BRed}${_ID}${NC}"

  # Look For Existing Assets and Delete As Necessary
  GH_ASSET="https://api.github.com/repos/${_OWNER}/${_REPO}/releases"
  EXISTING_ASSET="$(curl -s -H "Authorization: token ${_GITHUB_API_TOKEN}" "${GH_ASSET}")"

  if jq -e .[0].assets[0] <<< "${EXISTING_ASSET}" > /dev/null; then
    EXISTING_ASSET="$(jq .[0].assets[0].url -r <<< "${EXISTING_ASSET}")"
    curl -s -X DELETE -H "Authorization: token ${_GITHUB_API_TOKEN}" "${EXISTING_ASSET}"
    echo -e "${BGreen}Deleted Asset:${NC} ${BRed}${EXISTING_ASSET}${NC}"
  fi

  # Upload New Assets
  GH_ASSET="https://uploads.github.com/repos/${_OWNER}/${_REPO}/releases/${_ID}/assets?name=$(basename ${_FILENAME})"
  ASSET=$(curl -s --data-binary @"${_FILENAME}" -H "Authorization: token ${_GITHUB_API_TOKEN}" -H "Content-Type: application/octet-stream" "${GH_ASSET}" | jq .url -r)

  # Pretty Print Result
  echo -e "${BGreen}Uploaded:${NC} ${BRed}${ASSET}${NC}"
}

parse_args() {

  for LINE in "$@"; do
    eval "${LINE}"
  done

}

parse_args "$@"
main
