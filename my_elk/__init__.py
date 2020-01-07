import os
from enum import Enum

class Schema(Enum):
    BUILD = 1
    RUN = 2  
    PULL = 3

config_schemas = {
    Schema.RUN: {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "image": {
                    "type": "string"
                },
                "command": {
                    "type": ["string", "array"]
                },
                "auto_remove": {
                    "type": "boolean"
                },
                "detach": {
                    "type": "boolean"
                },
                "entrypoint": {
                    "type": ["string", "array"]
                },
                "environment": {
                    "type": ["object", "array"]
                },
                "hostname": {
                    "type": "string"
                },
                "links": {
                    "type": "object"
                },
                "mounts": {
                    "type": "array"
                },
                "name": {
                    "type": "string"
                },
                "network": {
                    "type": "string"
                },
                "privileged": {
                    "type": "boolean"
                },
                "ports": {
                    "type": "object"
                },
                "remove": {
                    "type": "boolean"
                },
                "user": {
                    "type": ["string", "number"]
                },
                "volumes": {
                    "type": ["object", "array"]
                }
            },
            "required": ["image"]
        }
    },
    Schema.BUILD: {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string"
                },
                "tag": {
                    "type": "string"
                },
                "dockerfile": {
                    "type": "string"
                },
                "rm": {
                    "type": "boolean"
                }
            },
            "required": ["path"]
        }
    },
    Schema.PULL: {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "repository": {
                    "type": "string"
                },
                "tag": {
                    "type": "string"
                }
            },
            "required": ["repository"]
        }
    }
}

import mysys.logger
import mysys.dockerize
