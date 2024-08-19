# stolen from https://github.com/hashicorp/terraform/issues/8344

data "archive_file" "custom_action" {
  count = var.source_directory_location != null ? 1 : 0

  type             = "zip"
  source_dir       = var.source_directory_location
  output_path      = "${path.module}/lambda_function_custom_actions.zip" # include name to prevent overwrite when module is reused
  output_file_mode = "0666"                                              # cross platform consistent output
}
