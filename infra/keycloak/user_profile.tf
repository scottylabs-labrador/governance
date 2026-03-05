resource "keycloak_realm_user_profile" "userprofile" {
  realm_id = keycloak_realm.labrador.id

  attribute {
    name         = "username"
    display_name = "$${username}"


    permissions {
      view = ["admin", "user"]
      edit = ["admin"]
    }
  }

  attribute {
    name         = "email"
    display_name = "$${email}"

    permissions {
      view = ["admin", "user"]
      edit = ["admin"]
    }
  }

  attribute {
    name         = "fullEmail"
    display_name = "Full Email"

    permissions {
      view = ["admin", "user"]
      edit = ["admin"]
    }
  }

  attribute {
    name         = "firstName"
    display_name = "$${firstName}"

    permissions {
      view = ["admin", "user"]
      edit = ["admin"]
    }
  }

  attribute {
    name         = "middleName"
    display_name = "Middle Name"


    permissions {
      view = ["admin", "user"]
      edit = ["admin"]
    }
  }

  attribute {
    name         = "lastName"
    display_name = "$${lastName}"

    permissions {
      view = ["admin", "user"]
      edit = ["admin"]
    }
  }

  attribute {
    name         = "fullName"
    display_name = "Full Name"


    permissions {
      view = ["admin", "user"]
      edit = ["admin"]
    }
  }

  attribute {
    name         = "displayName"
    display_name = "Display Name"


    permissions {
      view = ["admin", "user"]
      edit = ["admin"]
    }
  }

  # --- CMU Extended Metadata ---
  attribute {
    name         = "orcid"
    display_name = "ORCID"


    permissions {
      view = ["admin", "user"]
      edit = ["admin"]
    }
  }

  attribute {
    name         = "primaryAffiliation"
    display_name = "Primary Affiliation"


    permissions {
      view = ["admin", "user"]
      edit = ["admin"]
    }
  }

  attribute {
    name         = "affiliations"
    display_name = "Affiliations"

    permissions {
      view = ["admin", "user"]
      edit = ["admin"]
    }
  }

  attribute {
    name         = "departments"
    display_name = "Departments"

    permissions {
      view = ["admin", "user"]
      edit = ["admin"]
    }
  }

  attribute {
    name         = "colleges"
    display_name = "Colleges"

    permissions {
      view = ["admin", "user"]
      edit = ["admin"]
    }
  }

  attribute {
    name         = "level"
    display_name = "Level"


    permissions {
      view = ["admin", "user"]
      edit = ["admin"]
    }
  }

  attribute {
    name         = "class"
    display_name = "Class"


    permissions {
      view = ["admin", "user"]
      edit = ["admin"]
    }
  }

  attribute {
    name         = "status"
    display_name = "Status"


    permissions {
      view = ["admin", "user"]
      edit = ["admin"]
    }
  }

  group {
    name                = "user-metadata"
    display_header      = "User metadata"
    display_description = "Attributes, which refer to user metadata"
  }
}
