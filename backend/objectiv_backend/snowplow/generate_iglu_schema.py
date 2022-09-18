import os
import json5  # type: ignore
import json

from typing import List, Dict, Tuple, Any
# import objectiv -> snowplow-iglu version from config
from objectiv_backend.common.config import map_schema_version_to_snowplow

"""
Script to generate iglu schemas used to map the Objectiv Event objects to Snowplow, based on the 
Objectiv Taxonomy Schema. Resulting schemas will be under `iglu/`
"""


def get_properties_for_context(schema: Dict[str, Any], context_type: str, hierarchy: Dict[str, list]) -> \
        Tuple[Dict[str, dict], List[str]]:
    """
    recursively get all properties for a context, by traversing the hierarchy until there are no parents
    :param schema:
    :param context_type:
    :param hierarchy:
    :return: dictionary describing all object properties and a list of required ones
    """
    properties = {}
    required_properties = []

    # check if we have any parents
    if context_type in hierarchy:
        parents = hierarchy[context_type]
        for parent in parents:
            _properties, _require_properties = get_properties_for_context(schema, parent, hierarchy)
            properties.update(_properties)
            required_properties += _require_properties

    context = schema['contexts'][context_type]
    if 'properties' in context:
        for property_name in context['properties']:

            context_property_type = context['properties'][property_name]['type']
            # if optional is not set, we assume this property is required
            if 'optional' not in context['properties'][property_name] or \
                    not context['properties'][property_name]['optional']:
                property_type = [context_property_type]

                if property_name not in required_properties:
                    required_properties.append(property_name)
            else:
                # to mimic the optional properties, we add 'null' as type
                property_type = [context_property_type, 'null']
            properties[property_name] = {
                "type": property_type,
                "description": clean(context['properties'][property_name]['description'])
            }

    return properties, required_properties


def get_sp_iglu_schema(name: str, description: str, version: str, vendor: str, properties: dict,
                       required_properties: list, additional_properties: bool = True) -> str:
    """
    Generate iglu schema
    :param name: name of object
    :param description:
    :param version: iglu schema version to use (eg  1-0-0)
    :param vendor: vendor dir holding the schema (eg. io.objectiv.context)
    :param properties: dictionary with properties of the object
    :param required_properties:  list of required properties
    :param additional_properties: do we allow additional properties
    :return: json string
    """
    return json.dumps({
        "$schema": "http://iglucentral.com/schemas/com.snowplowanalytics.self-desc/schema/jsonschema/1-0-0#",
        "description": description,
        "self": {
            "vendor": vendor,
            "name": name,
            "format": "jsonschema",
            "version": version
        },
        "type": "object",
        "properties": properties,
        "additionalProperties": additional_properties,
        "required": required_properties
    }, indent=4)


def get_hierarchy(schema: Dict[str, Any]) -> Dict[str, List]:
    """
    returns a dictionary with context -> parents
    :param schema:
    :return:
    """
    hierarchy = {}

    for context_type, context in schema['contexts'].items():
        if 'parents' in context:
            hierarchy[context_type] = context['parents']

    return hierarchy


def clean(desc: str) -> str:
    """
    convenience function to remove whitespace
    :param desc:
    :return: str
    """
    return ' '.join(desc.split())


def generate_iglu_schema(schema_file: str, output_dir: str):
    with open(schema_file, 'r') as sfd:
        schema_data = sfd.read()

        schema = json5.loads(schema_data)
        hierarchy = get_hierarchy(schema)
        version = map_schema_version_to_snowplow(schema['version']['base_schema'])

        # write iglu schemas for all contexts
        vendor = 'io.objectiv.context'
        for context_type, context in schema['contexts'].items():
            print(f'found context: {context_type}')

            iglu_schema_file = os.path.join(output_dir, vendor, context_type, 'jsonschema', version)
            iglu_schema_dir = os.path.dirname(iglu_schema_file)
            os.makedirs(iglu_schema_dir, exist_ok=True)

            description = clean(context['description'])
            properties, required_properties = get_properties_for_context(schema, context_type, hierarchy)

            # if the _type property is set, we remove it here. The context type can be inferred from the column
            # name, so this is rather redundant.
            if '_type' in properties:
                del properties['_type']
            required_properties = [p for p in required_properties if p != '_type']
            
            sp_schema = get_sp_iglu_schema(name=context_type, description=description, version=version, vendor=vendor,
                                           properties=properties, required_properties=required_properties)
            with open(iglu_schema_file, 'w+') as sp_schema_file:
                sp_schema_file.write(sp_schema)

        # write iglu schema for location_stack
        vendor = 'io.objectiv'
        iglu_schema_file = os.path.join(output_dir, vendor, 'location_stack', 'jsonschema', version)
        iglu_schema_dir = os.path.dirname(iglu_schema_file)
        os.makedirs(iglu_schema_dir, exist_ok=True)
        with open(iglu_schema_file, 'w+') as sp_schema_file:
            event = schema['events']['AbstractEvent']
            location_stack = event['properties']['location_stack']
            description = clean(location_stack['description'])
            properties = {
                'location_stack': {
                    'type': 'array',
                    'description': description,
                    'minItems': 1
                }
            }
            required_properties = ['location_stack']
            sp_schema = get_sp_iglu_schema(name='location_stack', description=description, version=version,
                                           vendor=vendor, properties=properties, required_properties=required_properties)
            sp_schema_file.write(sp_schema)


if __name__ == "__main__":
    generate_iglu_schema(schema_file='../schema/base_schema.json5',
                         output_dir=os.path.join(os.path.dirname(__file__), 'iglu'))
