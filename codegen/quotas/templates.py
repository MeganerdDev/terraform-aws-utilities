import re


def get_variable_name(service_code, quota_name):
    variable_name = f"{service_code}_{quota_name}".lower()
    return re.sub(r'\W+', '_', variable_name)

def terraform_variable_template(service_code, quota_name, quota_code):
    variable_name = get_variable_name(service_code, quota_name)
    return f'''variable "{variable_name}" {{
  description = "Quota for [{service_code}]: {quota_name} ({quota_code})"
  type        = number
  default     = null
}}\n\n'''

def terraform_locals_template(service_code, quota_name, quota_code):
    variable_name = get_variable_name(service_code, quota_name)
    return f'''    {variable_name} = {{
      quota_code    = "{quota_code}"
      service_code  = "{service_code}"
      desired_quota = var.{variable_name}
    }},\n'''

def terraform_main(all_quotas):
    return f'''# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONFIGURE SERVICE QUOTAS
# NOTE: This module is autogenerated. Do not modify it manually.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

terraform {{
  required_version = ">= 1.0.0"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = ">= 3.75.1, < 6.0.0"
    }}
  }}
}}

locals {{
  all_quotas = {{
{all_quotas}
  }}

  adjusted_quotas = {{
    for k, v in local.all_quotas : k => v
    if v.desired_quota != null
  }}
}}

resource "aws_servicequotas_service_quota" "increase_quotas" {{
  for_each = local.adjusted_quotas

  quota_code   = each.value.quota_code
  service_code = each.value.service_code
  value        = each.value.desired_quota
}}

'''

def terraform_vars(all_vars):
    return f'''# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# INPUT VARIABLES FOR SERVICE QUOTAS
# NOTE: This module is autogenerated. Do not modify it manually.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

{all_vars}

\n'''