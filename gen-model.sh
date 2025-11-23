#!/usr/bin/env bash
# Generate Pydantic models automatically from JSON files
# Depends on `datamodel-code-generator` (https://github.com/koxudaxi/datamodel-code-generator) package

set -euo pipefail
IFS=$'\n\t'

SUCCESS_EXIT=0
ERR_EXIT=1

MODELS_DIR="${PWD}/akcli/models/"
OUTPUT_MODEL_TYPE="pydantic_v2.BaseModel"
BASE_CLASS=".base_response.CamelCaseModel"


_show_help() {
    prog_name=$(basename "$0")
    cat << EOF
Usage: ${prog_name} -i INPUT_FILE -o OUTPUT_FILE [OPTIONS]

Generate Pydantic models from JSON schema files.

Options:
    -i, --input         Input JSON file path (required)
    -o, --output        Output Python file name (required)
    -H, --file-headers  Additional text to prepend to file headers (optional)
    -h, --help          Show this help message

Example:
    ${prog_name} -i example.json -o example_model.py
    ${prog_name} -i example.json -o example_model.py -H "Custom header text"
EOF
    exit $SUCCESS_EXIT
}

_get_file_headers() {
    local additional="$1"
    # add a newline to additional headers if they exist
    if [ -n "$additional" ]; then
        additional="${additional}"$'\n'
    fi

    cat <<EOF
#/usr/bin/env python3

"""
${additional}Generated with \`datamodel-code-generator\` (https://github.com/koxudaxi/datamodel-code-generator)
and refined with manual adjustments.
"""
EOF
}

_validate_args() {
    local input_file="$1"
    local output_file="$2"

    if [ -z "${input_file}" ] || [ -z "${output_file}" ]; then
        echo "error: Both --input and --output are required."
        exit $ERR_EXIT
    fi

    if [ ! -f "${input_file}" ]; then
        echo "error: Input file '${input_file}' does not exist."
        exit $ERR_EXIT
    fi
}

main() {
    if [ $# -eq 0 ]; then
        show_help
    fi

    INPUT_FILE=""
    OUTPUT_FILE=""
    ADDITIONAL_HEADERS=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            -i|--input)
                INPUT_FILE="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_FILE="$2"
                shift 2
                ;;
            -H|--file-headers)
                ADDITIONAL_HEADERS="$2"
                shift 2
                ;;
            -h|--help)
                _show_help
                ;;
            *)
                echo "error: Unknown option: $1"
                exit $ERR_EXIT
                ;;
        esac
    done

    _validate_args "${INPUT_FILE}" "${OUTPUT_FILE}"

    FILE_HEADERS="$(_get_file_headers "${ADDITIONAL_HEADERS}")"

    datamodel-codegen \
        --input "${INPUT_FILE}" \
        --output "${MODELS_DIR}/${OUTPUT_FILE}" \
        --input-file-type json \
        --output-model-type "${OUTPUT_MODEL_TYPE}" \
        --base-class "${BASE_CLASS}" \
        --use-annotated \
        --custom-file-header "${FILE_HEADERS}" \
        --field-constraints \
        --snake-case-field \
        --force-optional \
        --no-alias

    exit $SUCCESS_EXIT
}

main "$@"
