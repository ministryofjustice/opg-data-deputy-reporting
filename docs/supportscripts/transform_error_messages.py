import json
from pprint import pprint

swagger_errors = {
    "Error400": {
        "type": "object",
        "required": ["errors"],
        "properties": {
            "errors": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["code", "title"],
                    "properties": {
                        "id": {"type": "string", "example": "A123BCD"},
                        "code": {
                            "type": "string",
                            "example": "OPGDATA-API-INVALIDREQUEST",
                        },
                        "title": {"type": "string", "example": "Invalid Request"},
                        "detail": {
                            "type": "string",
                            "example": "Invalid request, the data is incorrect",
                        },
                        "meta": {
                            "type": "object",
                            "properties": {
                                "x-ray": {
                                    "type": "string",
                                    "example": "93c330d4-7d84-4c1b-8fdb-54cec5bfe747",
                                }
                            },
                        },
                    },
                },
            }
        },
    },
    "Error401": {
        "type": "object",
        "required": ["errors"],
        "properties": {
            "errors": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["code", "title"],
                    "properties": {
                        "id": {"type": "string", "example": "A123BCD"},
                        "code": {
                            "type": "string",
                            "example": "OPGDATA-API-UNAUTHORISED",
                        },
                        "title": {
                            "type": "string",
                            "example": "User is not authorised",
                        },
                        "detail": {
                            "type": "string",
                            "example": "Unauthorised (no current user and there should be)",
                        },
                        "meta": {
                            "type": "object",
                            "properties": {
                                "x-ray": {
                                    "type": "string",
                                    "example": "93c330d4-7d84-4c1b-8fdb-54cec5bfe747",
                                }
                            },
                        },
                    },
                },
            }
        },
    },
    "Error403": {
        "type": "object",
        "required": ["errors"],
        "properties": {
            "errors": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["code", "title"],
                    "properties": {
                        "id": {"type": "string", "example": "A123BCD"},
                        "code": {"type": "string", "example": "OPGDATA-API-FORBIDDEN"},
                        "title": {"type": "string", "example": "Access Denied"},
                        "detail": {
                            "type": "string",
                            "example": "Forbidden - The current user is forbidden from accessing this data (in this way)",
                        },
                        "meta": {
                            "type": "object",
                            "properties": {
                                "x-ray": {
                                    "type": "string",
                                    "example": "93c330d4-7d84-4c1b-8fdb-54cec5bfe747",
                                }
                            },
                        },
                    },
                },
            }
        },
    },
    "Error404": {
        "type": "object",
        "required": ["errors"],
        "properties": {
            "errors": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["code", "title"],
                    "properties": {
                        "id": {"type": "string", "example": "A123BCD"},
                        "code": {"type": "string", "example": "OPGDATA-API-NOTFOUND"},
                        "title": {"type": "string", "example": "Page not found"},
                        "detail": {
                            "type": "string",
                            "example": "That URL is not a valid route, or the item resource does not exist",
                        },
                        "meta": {
                            "type": "object",
                            "properties": {
                                "x-ray": {
                                    "type": "string",
                                    "example": "93c330d4-7d84-4c1b-8fdb-54cec5bfe747",
                                }
                            },
                        },
                    },
                },
            }
        },
    },
    "Error413": {
        "type": "object",
        "required": ["errors"],
        "properties": {
            "errors": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["code", "title"],
                    "properties": {
                        "id": {"type": "string", "example": "A123BCD"},
                        "code": {
                            "type": "string",
                            "example": "OPGDATA-API-FILESIZELIMIT",
                        },
                        "title": {"type": "string", "example": "Payload too large"},
                        "detail": {
                            "type": "string",
                            "example": "Payload too large, try and upload in smaller chunks",
                        },
                        "meta": {
                            "type": "object",
                            "properties": {
                                "x-ray": {
                                    "type": "string",
                                    "example": "93c330d4-7d84-4c1b-8fdb-54cec5bfe747",
                                }
                            },
                        },
                    },
                },
            }
        },
    },
    "Error415": {
        "type": "object",
        "required": ["errors"],
        "properties": {
            "errors": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["code", "title"],
                    "properties": {
                        "id": {"type": "string", "example": "A123BCD"},
                        "code": {"type": "string", "example": "OPGDATA-API-MEDIA"},
                        "title": {
                            "type": "string",
                            "example": "Unsupported media type",
                        },
                        "detail": {
                            "type": "string",
                            "example": "Unsupported media type for this endpoint",
                        },
                        "meta": {
                            "type": "object",
                            "properties": {
                                "x-ray": {
                                    "type": "string",
                                    "example": "93c330d4-7d84-4c1b-8fdb-54cec5bfe747",
                                }
                            },
                        },
                    },
                },
            }
        },
    },
    "Error500": {
        "type": "object",
        "required": ["errors"],
        "properties": {
            "errors": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["code", "title"],
                    "properties": {
                        "id": {"type": "string", "example": "A123BCD"},
                        "code": {
                            "type": "string",
                            "example": "OPGDATA-API-SERVERERROR",
                        },
                        "title": {"type": "string", "example": "Internal server error"},
                        "detail": {
                            "type": "string",
                            "example": "Something unexpected happened internally",
                        },
                        "meta": {
                            "type": "object",
                            "properties": {
                                "x-ray": {
                                    "type": "string",
                                    "example": "93c330d4-7d84-4c1b-8fdb-54cec5bfe747",
                                }
                            },
                        },
                    },
                },
            }
        },
    },
    "Error503": {
        "type": "object",
        "required": ["errors"],
        "properties": {
            "errors": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["code", "title"],
                    "properties": {
                        "id": {"type": "string", "example": "A123BCD"},
                        "code": {
                            "type": "string",
                            "example": "OPGDATA-API-UNAVAILABLE",
                        },
                        "title": {"type": "string", "example": "Service Unavailable"},
                        "detail": {
                            "type": "string",
                            "example": "Service is currently unavailable. Please try again later",
                        },
                        "meta": {
                            "type": "object",
                            "properties": {
                                "x-ray": {
                                    "type": "string",
                                    "example": "93c330d4-7d84-4c1b-8fdb-54cec5bfe747",
                                }
                            },
                        },
                    },
                },
            }
        },
    },
}


errors = {}

for k, v in swagger_errors.items():
    status_code = k[5:]
    error_code = v["properties"]["errors"]["items"]["properties"]["code"]["example"]
    error_title = v["properties"]["errors"]["items"]["properties"]["title"]["example"]
    error_message = v["properties"]["errors"]["items"]["properties"]["detail"][
        "example"
    ]

    errors[status_code] = {
        "error_code": error_code,
        "error_title": error_title,
        "error_message": error_message,
    }


pprint(errors)
