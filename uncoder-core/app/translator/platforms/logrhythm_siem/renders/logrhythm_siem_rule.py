"""
Uncoder IO Community Edition License
-----------------------------------------------------------------
Copyright (c) 2024 SOC Prime, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-----------------------------------------------------------------
"""
import ast
import copy
from datetime import datetime, timedelta
import json
import random
import re
import traceback
from typing import Optional

from app.translator.core.custom_types.meta_info import SeverityType
from app.translator.core.mapping import SourceMapping
from app.translator.core.models.platform_details import PlatformDetails
from app.translator.core.models.query_container import MetaInfoContainer
from app.translator.managers import render_manager
from app.translator.platforms.logrhythm_siem.const import DEFAULT_LOGRHYTHM_Siem_RULE, logrhythm_siem_rule_details
from app.translator.platforms.logrhythm_siem.escape_manager import logrhythm_rule_escape_manager
from app.translator.platforms.logrhythm_siem.renders.logrhythm_siem_query import (
    # LogRhythmSiemFieldValue
    LogRhythmSiemFieldValue,
    LogRhythmSiemQueryRender,
)
from app.translator.tools.utils import get_rule_description_str

_AUTOGENERATED_TEMPLATE = "Autogenerated LogRhythm Siem Rule"
_SEVERITIES_MAP = {
    SeverityType.critical: SeverityType.critical,
    SeverityType.high: SeverityType.high,
    SeverityType.medium: SeverityType.medium,
    SeverityType.low: SeverityType.low,
    SeverityType.informational: SeverityType.low,
}


class LogRhythmSiemRuleFieldValue(LogRhythmSiemFieldValue):
    details: PlatformDetails = logrhythm_siem_rule_details
    escape_manager = logrhythm_rule_escape_manager


@render_manager.register
class LogRhythmSiemRuleRender(LogRhythmSiemQueryRender):
# class LogRhythmSiemRuleRender():
    details: PlatformDetails = logrhythm_siem_rule_details
    or_token = "or"
    field_value_map = LogRhythmSiemRuleFieldValue(or_token=or_token)


    # Function to generate ISO 8601 formatted date within the last 24 hours
    def generate_iso_date(self):
        now = datetime.utcnow()
        past_date = now - timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59), seconds=random.randint(0, 59))
        return past_date.isoformat() + 'Z'


    def generate_timestamps(self):
        iso_date = self.generate_iso_date()
        date_created = iso_date
        date_saved = iso_date
        date_used = iso_date
        date_used = (date_used.split('.')[0]) + "Z"
        return_obj = []

        return_obj.append(date_created)
        return_obj.append(date_saved)
        return_obj.append(date_used)
        return return_obj


    def finalize_query(
        self,
        prefix: str,
        query: str,
        functions: str,
        meta_info: Optional[MetaInfoContainer] = None,
        source_mapping: Optional[SourceMapping] = None,
        not_supported_functions: Optional[list] = None,
        *args,  # noqa: ARG002
        **kwargs,  # noqa: ARG002
    ) -> str:
        query = super().finalize_query(prefix=prefix, query=query, functions=functions)
        rule = copy.deepcopy(DEFAULT_LOGRHYTHM_Siem_RULE)
        ''' Parse out query - originally for "filter".
            example how it should look like:
            {
                "filterItemType": 0,
                "fieldOperator": 0,
                "filterMode": 1,
                "filterType": 29, # Must be altered
                "values": [
                    {
                        "filterType": 29, # Must be altered
                        "valueType": 4,
                        "value": {
                            "value": "moo",
                            "matchType": 0
                        },
                        "displayValue": "moo"
                    }
                ],
                "name": "User (Origin)"
            }

            ANDs & CONTAINS needs to be broken out
        '''
        # rule["queryFilter"]["filterGroup"]["raw"] = query # DEBUG
        query = self.gen_filter_item(query)
        # rule["observationPipeline"]["pattern"]["operations"][0]["logObserved"]["filter"] = query
        rule["queryFilter"]["filterGroup"]["filterItems"] = query
        
        rule["title"] = meta_info.title or _AUTOGENERATED_TEMPLATE
        rule["description"] = get_rule_description_str(
            description=meta_info.description or rule["description"] or _AUTOGENERATED_TEMPLATE,
            author=meta_info.author,
            license_=meta_info.license,
        )

        # Set the time, default is last 24 hours
        gen_time = self.generate_timestamps()
        rule["dateCreated"] = gen_time[0]
        rule["dateSaved"] = gen_time[1]
        rule["dateUsed"] = gen_time[2]

        json_rule = json.dumps(rule, indent=4, sort_keys=False)
        if not_supported_functions:
            rendered_not_supported = self.render_not_supported_functions(not_supported_functions)
            return json_rule + rendered_not_supported
        return json_rule


    def pull_filter_item(self, f_type):
        if f_type == 'User (Origin)':
            f_type = 'Login'
        
        filter_type = {
            'IDMGroupForAccount': 53,
            'Address': 44,
            'Amount': 64,
            'Application': 97,
            'MsgClass': 10,
            'Command': 112,
            'CommonEvent': 11,
            'Direction': 2,
            'Duration': 62,
            'Group': 38,
            'BytesIn': 58,
            'BytesOut': 59,
            'BytesInOut': 95,
            'DHost': 100,
            'Host': 98,
            'SHost': 99,
            'ItemsIn': 60,
            'ItemsOut': 61,
            'ItemsInOut': 96,
            'DHostName': 25,
            'HostName': 23,
            'SHostName': 24,
            'KnownService': 16,
            'DInterface': 108,
            'Interface': 133,
            'SInterface': 107,
            'DIP': 19,
            'IP': 17,
            'SIP': 18,
            'DIPRange': 22,
            'IPRange': 20,
            'SIPRange': 21,
            'KnownDHost': 15,
            'KnownHost': 13,
            'KnownSHost': 14,
            'Location': 87,
            'SLocation': 85,
            'DLocation': 86,
            'MsgSource': 7,
            'Entity': 6,
            'RootEntity': 136,
            'MsgSourceType': 9,
            'DMAC': 104,
            'MAC': 132,
            'SMAC': 103,
            'Message': 35,
            'MPERule': 12,
            'DNATIP': 106,
            'NATIP': 126,
            'SNATIP': 105,
            'DNATIPRange': 125,
            'NATIPRange': 127,
            'SNATIPRange': 124,
            'DNATPort': 115,
            'NATPort': 130,
            'SNATPort': 114,
            'DNATPortRange': 129,
            'NATPortRange': 131,
            'SNATPortRange': 128,
            'DNetwork': 50,
            'Network': 51,
            'SNetwork': 49,
            'Object': 34,
            'ObjectName': 113,
            'Login': 29,
            'IDMGroupForLogin': 52,
            'Priority': 3,
            'Process': 41,
            'PID': 109,
            'Protocol': 28,
            'Quantity': 63,
            'Rate': 65,
            'Recipient': 32,
            'Sender': 31,
            'Session': 40,
            'Severity': 110,
            'Size': 66,
            'Subject': 33,
            'DPort': 27,
            'Port': 45,
            'SPort': 26,
            'DPortRange': 47,
            'PortRange': 48,
            'SPortRange': 46,
            'URL': 42,
            'Account': 30,
            'User': 43,
            'IDMGroupForUser': 54,
            'VendorMsgID': 37,
            'Version': 111,
            'SZone': 93,
            'DZone': 94,
            'FilterGroup': 1000,
            'PolyListItem': 1001,
            'Domain': 39,
            'DomainOrigin': 137,
            'Hash': 138,
            'Policy': 139,
            'VendorInfo': 140,
            'Result': 141,
            'ObjectType': 142,
            'CVE': 143,
            'UserAgent': 144,
            'ParentProcessId': 145,
            'ParentProcessName': 146,
            'ParentProcessPath': 147,
            'SerialNumber': 148,
            'Reason': 149,
            'Status': 150,
            'ThreatId': 151,
            'ThreatName': 152,
            'SessionType': 153,
            'Action': 154,
            'ResponseCode': 155,
            'UserOriginIdentityID': 167,
            'Identity': 160,
            'UserImpactedIdentityID': 168,
            'SenderIdentityID': 169,
            'RecipientIdentityID': 170
            }

        value_type = {
        'Byte': 0,
        'Int16': 1,
        'Int32': 2,
        'Int64': 3,
        'String': 4,
        'IPAddress': 5,
        'IPAddressrange': 6,
        'TimeOfDay': 7,
        'DateRange': 8,
        'PortRange': 9,
        'Quantity': 10,
        'ListReference': 11,
        'ListSet': 12,
        'Null': 13,
        'INVALID': 99
        }
        if f_type in filter_type:
            r_f = filter_type[f_type]
        else:
            print(f'filterType name reference was not found: {f_type}')
            r_f = 0000
        # v_t = value_type[v_type]
        return r_f
    

    def process_sub_conditions(self, sub_conditions, items):
        parsed_conditions = []
        for sub_condition in sub_conditions:
            try:
                # Parse the sub_condition
                # This generally is preventing many things from parsing properly
                if sub_condition.startswith('target.host.network_port.value') or \
                        sub_condition.startswith('general_information.log_source.type_name CONTAINS target.host.network_port.value'):
                    sub_condition = sub_condition.replace('general_information.log_source.type_name CONTAINS ','')
                    matches = re.findall(r'(target\.host\.network_port\.value) in \[([^\]]+)\]', sub_condition)
                    if matches:
                        for match in matches:
                            # lrTODO : this needs to go into process_match
                            # items = self.process_match(match)
                            field, value = match
                            f_t = self.field_translation(field)
                            port_list = [int(x.strip()) for x in value.split(',')]
                            for port in port_list:
                                items.append({
                                    "filterType": self.pull_filter_item(f_t),
                                    "valueType": 4,
                                    "value": {
                                        "value": port,
                                        "matchType": 0
                                    },
                                    "displayValue": f_t
                                })
                elif 'CONTAINS' in sub_condition:
                    print(f'CONTAINS sub_condition: {sub_condition}')
                    try:
                        matches = re.findall(r'(\w+\.\w+\.\w+) CONTAINS "([^"]+)"', sub_condition)[0]
                    except:
                        matches = re.findall(r'(\w+\.\w+\.\w+) CONTAINS "([^"]+)"', sub_condition)
                    if not matches:
                        matches = re.findall(r'(\w+\.\w+) CONTAINS "([^"]+)"', sub_condition)
                    if 'matches ' in sub_condition:
                        match = matches[0]
                        # Some instances have a matches after a contains,
                        s_match = sub_condition.split('matches ')[1]
                        s_c_filtered = s_match.replace('"','').replace('.*','')
                        result = (match, s_c_filtered)
                        # result = (match, match + s_c_filtered)
                        f_t = self.field_translation(result[0])
                        v_t = result[1]
                        if result[0] in result[1]: 
                            v_t = v_t.replace(result[0],'')
                        items.append({
                            "filterType": self.pull_filter_item(v_t),
                            "valueType": 4,
                            "value": {
                                "value": result[1].replace('\\', '/'),
                                "matchType": 0
                            },
                            "displayValue": f_t
                        })
                    if len(matches) == 2:
                        f_t = self.field_translation(matches[0])
                        items.append({
                            "filterType": self.pull_filter_item(f_t),
                            "valueType": 4,
                            "value": {
                                "value": matches[1].replace('\\', '/'),
                                "matchType": 0
                            },
                            "displayValue": f_t
                        })
                    else:
                        for match in matches:
                            items = self.process_match(match)
                      
                # Parse the sub_condition
                elif 'AND' in sub_condition:
                    print(f'AND sub_condition: {sub_condition} length={len(sub_condition)}')
                    matches = re.findall(r'(\w+\.\w+\.\w+) AND "([^"]+)"', sub_condition)
                    if not matches:
                        matches = re.findall(r'(\w+\.\w+\.\w+) matches ([^\s]+)', sub_condition)
                    # field, value = re.findall(r'(\w+\.\w+\.\w+) CONTAINS "([^"]+)"', sub_condition)[0]
                    if matches:
                        if len(matches) == 2:
                            f_t = self.field_translation(matches[0][0])
                            f_v = matches[0][1]
                            f_v = f_v.replace('\"','')
                            items.append({
                                "filterType": self.pull_filter_item(f_t),
                                "valueType": 4,
                                "value": {
                                    "value": f_v.replace('\\', '/'),
                                    "matchType": 0
                                },
                                "displayValue": f_t
                            })
                        else:
                            for match in matches:
                                items = self.process_match(match)
                elif 'matches' in sub_condition:
                    matches = re.findall(r'(\w+\.\w+\.\w+) matches "([^"]+)"', sub_condition)
                    if matches:
                        for match in matches:
                            items = self.process_match(match)
                elif 'origin.account.name' in sub_condition or 'User' in sub_condition:
                    if 'User' in sub_condition:
                        matches = re.findall(r'User: "([^"]+)"', sub_condition)
                    else:
                        matches = re.findall(r'origin\.account\.name = "([^"]+)"', sub_condition)
                    if matches:
                        print(f'origin.account.name -> {matches}')
                        for match in matches:
                            items = self.process_match(match)
                elif 'object.file.name' in sub_condition or 'TargetFilename' in sub_condition:
                    if 'TargetFilename' in sub_condition:
                        matches = re.findall(r'TargetFilename: "([^"]+)"', sub_condition)
                    else:
                        matches = re.findall(r'object\.file\.name = "([^"]+)"', sub_condition)
                    if matches:
                        for match in matches:

                            items = self.process_match(match)
            except Exception as e:
                print(f'Error processing sub_condition: {sub_condition}')
                print(f'Error: {e}')
                traceback.print_exc()
        print(f'items END: {items}\nParsed_condition: {parsed_conditions}')
        return items
    


    def gen_filter_item(self, query):
        ''' Collection of general observations found that breaks translation '''
        # Removing the product[0] AND to be more global friendly with parsing
        query = query.replace("\\\'product\\\'", "'product'")
        query = query.replace('query_container.meta_info.parsed_logsources[\'product\'][0] AND ', '')

        # Random
        query = query.replace('anything AND ', '') # LR Siem cannot really handle this query

        # Remove outer parentheses
        # Split the query into individual conditions
        query = re.sub(r'^\(\(|\)\)$', '', query)
        print(f'Query Cleaned: {query}')
        conditions = re.split(r'\)\s*or \s*\(', query)
        parsed_conditions = []

        for condition in conditions:
            # Remove inner parentheses
            condition = condition.strip('()')
            condition = condition.replace('((', '')
            condition = condition.replace('(', '')
            sub_conditions = re.split(r'\s*or \s*', condition)
            # sub_conditions = re.split(r'\s*AND\s*', condition)
            items = []

            current_found = parsed_conditions.append(self.process_sub_conditions(sub_conditions, items))
            parsed_conditions.append(current_found)
        return parsed_conditions[0]


    def field_translation(self, field):
        if field == 'origin.account.name':
            field = 'User (Origin)'
        elif field == 'general_information.raw_message':
            field = 'Message'
        elif field in { 'object.process.command_line', 
                        'object.script.command_line'
                        }:
            field = 'Command'
        elif field in { 'object.registry_object.path', 
                       'object.registry_object.key', 
                       'object.resource.name'
                       }:
            field = 'Object'
        elif field in { 'target.host.ip_address.value',
                       'target.host.ip_address.value'
                       }:
            field = 'Address'
        elif field in { 'target.host.name',
                       'target.host.domain'
                       }:
            field = 'DHost'
        elif field in { 'action.network.byte_information.received',
                       'action.network.byte_information.received'
                       }:
            field = 'BytesIn'
        elif field == 'unattributed.host.mac_address':
            field = 'MAC'
        elif field == 'action.network.http_method':
            field = 'SIP'
        elif field in { 'origin.url.path', 
                       'action.dns.query'
                       }:
            field = 'URL'
        elif field == 'origin.host.domain':
            field = 'SHostName'
        elif field == 'target.host.domain':
            field = 'Host'
        elif field == 'action.network.byte_information.sent':
            field = 'BytesOut'
        elif field == 'action.network.byte_information.total':
            field = 'BytesInOut'
        elif field == 'object.process.name':
            field = 'Application'
        elif field == 'action.duration':
            field = 'Duration'
        elif field == 'process.parent_process.path':
            field = 'ParentProcessPath'
        elif field == 'object.process.parent_process.name':
            field = 'ParentProcessName'
        elif field == 'object.file.name' or field == 'TargetFilename':
            field = 'Object'
        elif field == 'target.host.network_port.value':
            field = 'Port'
        return field
    

    def process_match(self, match):
        field, value = match
        keywords = ["AND", "CONTAINS", "AND NOT", "IN", "NOT"]
        items = []
    
        # Regex to extract field and value
        # pattern = re.compile(r'(\S+)\s+(CONTAINS|NOT |IN|NOT IN|AND|OR)\s+(.+)')
        pattern = re.compile(r'((?:NOT \s+)?\S+)\s+(CONTAINS|in|IN|NOT IN|AND|OR|AND NOT|NOT)\s+(.+)')
    
        # Initial tuple block
        i_field = field
        i_block = value.split(' ')[0]
        i_block = i_block.replace('"','')
        i_v = (i_field, i_block)
        # i_block = re.split(f'\\s+{keyword}\\s+', value)
        # print(f'item append len : {len(i_v)}')
        items.extend(self.item_append(i_v))
        # Split the value based on the keywords
        for keyword in keywords:
            if keyword in value:
                parts = re.split(f'\\s+{keyword}\\s+', value)
                for part in parts:
                    part = part.strip()
                    if part:
                        # MUST match array list AND, CONTAINS, etc. otherwise skip
                        match_obj = pattern.match(part)
                        if match_obj == None and part.startswith('NOT '):
                            k = part.replace('NOT ','')
                            match_obj = pattern.match(k)
                        if match_obj:
                            # Construct a new match tuple and process it
                            new_field = match_obj.group(1)
                            # lr_TODO : clean value
                            new_value = match_obj.group(3)
                            current_match = (new_field, self.clean_value(new_value))
                            print(f'keyword current_match len: {len(current_match)}\nvalue: {current_match}')
                            items.extend(self.item_append(current_match))
                break
        else:
            # If no keywords are found, process the original match
            no_keywords = (field, value)
            print(f'else item append no keyword:{no_keywords}')
            items.extend(self.item_append(no_keywords))
    
        return items
    

    def clean_value(self, value):
        return_value = value.replace(')','')
        return return_value


    def item_append(self, match):
        items = []
        field, value = match
        f_t = self.field_translation(field=field)
        if f_t == 'Port':
            if isinstance(value, list) or value.startswith('[') and value.endswith(']'):
                value = self.check_array(value)
                port_list = [int(x.strip()) for x in value.split(',')]
                for port in port_list:
                    items.append(self.new_item(f_t=f_t, value=port))
            else:
                items.append(self.new_item(f_t=f_t, value=value))
        else:
            items.append(self.new_item(f_t=f_t, value=value))
        return items
    


    def new_item(self, f_t, value):
        # Clean if value is string, else just feed it through (could be port number)
        if isinstance(value, str):
            value = value.replace('\\', '/')
        i = {
                "filterType": self.pull_filter_item(f_t),
                "valueType": 4,
                "value": {
                    "value": value,
                    "matchType": 0
                },
                "displayValue": f_t
            }
        return i
    
        
    def check_array(self, s):
        if isinstance(s, str):
            if re.match(r'^\[.*\]$', s.strip()):
                try:
                    # Safely eval the str to a Py List
                    array = ast.literal_eval(s)
                    if isinstance(array, list):
                        return array
                except (ValueError, SyntaxError):
                    pass
            return None
        else:
            return s