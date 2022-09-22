from enum import Enum

from pydantic import BaseModel, HttpUrl, Field
from typing import List, Union, Dict, Any, Text, Callable, Set
import re
from requests import Request

Name = Text
Url = Text
BaseUrl = Union[HttpUrl, Text]
VariablesMapping = Dict[Text, Any]
FunctionsMapping = Dict[Text, Callable]
Headers = Dict[Text, Text]
Cookies = Dict[Text, Text]
Verify = bool
Hooks = List[Union[Text, Dict[Text, Text]]]
Export = List[Text]
Validators = List[Dict]
Env = Dict[Text, Any]


class MethodEnum(Text, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"


class ProtoType(Enum):
    Binary = 1
    CyBinary = 2
    Compact = 3
    Json = 4


class TransType(Enum):
    Buffered = 1
    CyBuffered = 2
    Framed = 3
    CyFramed = 4


# configs for thrift rpc
class TConfigThrift(BaseModel):
    psm: Text = None
    env: Text = None
    cluster: Text = None
    target: Text = None
    include_dirs: List[Text] = None
    thrift_client: Any = None
    timeout: int = 10
    idl_path: Text = None
    method: Text = None
    ip: Text = "127.0.0.1"
    port: int = 9000
    service_name: Text = None
    proto_type: ProtoType = ProtoType.Binary
    trans_type: TransType = TransType.Buffered


# configs for db
class TConfigDB(BaseModel):
    psm: Text = None
    user: Text = None
    password: Text = None
    ip: Text = None
    port: int = 3306
    database: Text = None


class TConfig(BaseModel):
    name: Name
    verify: Verify = False
    base_url: BaseUrl = ""
    # Text: prepare variables in debugtalk.py, ${gen_variables()}
    variables: Union[VariablesMapping, Text] = {}
    parameters: Union[VariablesMapping, Text] = {}
    # setup_hooks: Hooks = []
    # teardown_hooks: Hooks = []
    export: Export = []
    path: Text = None
    # configs for other protocols
    db: TConfigDB = TConfigDB()


class TRequest(BaseModel):
    """requests.Request model"""

    method: MethodEnum
    url: Url
    params: Dict[Text, Text] = {}
    headers: Headers = {}
    req_json: Union[Dict, List, Text] = Field(None, alias="json")   # json
    data: Union[Text, Dict[Text, Any]] = None
    cookies: Cookies = {}
    timeout: float = 120
    allow_redirects: bool = True
    verify: Verify = False
    upload: Dict = {}  # used for upload files


class TStep(BaseModel):
    name: Name
    request: Union[TRequest, None] = None
    testcase: Union[Text, Callable, None] = None
    variables: VariablesMapping = {}
    setup_hooks: Hooks = []
    teardown_hooks: Hooks = []
    # used to extract request's response field
    extract: VariablesMapping = {}
    # used to export session variables from referenced testcase
    export: Export = []
    validators: Validators = Field([], alias="validate")
    validate_script: List[Text] = []
    retry_times: int = 0
    retry_interval: int = 0  # sec


class RequestData(BaseModel):
    method: MethodEnum = MethodEnum.GET
    url: Url
    headers: Headers = {}
    cookies: Cookies = {}
    body: Union[Text, bytes, List, Dict, None] = {}


class ResponseData(BaseModel):
    status_code: int
    headers: Dict
    cookies: Cookies
    encoding: Union[Text, None] = None
    content_type: Text
    body: Union[Text, bytes, List, Dict, None]


class ReqRespData(BaseModel):
    request: RequestData
    response: ResponseData


class RequestStat(BaseModel):
    content_size: float = 0
    response_time_ms: float = 0
    elapsed_ms: float = 0


class AddressData(BaseModel):
    client_ip: Text = "N/A"
    client_port: int = 0
    server_ip: Text = "N/A"
    server_port: int = 0


class SessionData(BaseModel):
    """request session data, including request, response, validators and stat data"""

    success: bool = False
    # in most cases, req_resps only contains one request & response
    # while when 30X redirect occurs, req_resps will contain multiple request & response
    req_resps: List[ReqRespData] = []
    stat: RequestStat = RequestStat()
    address: AddressData = AddressData()
    validators: Dict = {}


class StepResult(BaseModel):
    """teststep data, each step maybe corresponding to one request or one testcase"""

    name: Text = ""  # teststep name
    step_type: Text = ""  # teststep type, request or testcase
    success: bool = False
    data: Union[SessionData, List["StepResult"]] = None
    elapsed: float = 0.0  # teststep elapsed time
    content_size: float = 0  # response content size
    export_vars: VariablesMapping = {}
    attachment: Text = ""  # teststep attachment


class TestCase(BaseModel):
    config: TConfig
    test_steps: List[TStep]



if __name__ == "__main__":
    # use $$ to escape $ notation
    dolloar_regex_compile = re.compile(r"\$\$")
    # variable notation, e.g. ${var} or $var
    # variable should start with a-zA-Z_
    variable_regex_compile = re.compile(r"\$\{([a-zA-Z_]\w*)\}|\$([a-zA-Z_]\w*)")
    # function notation, e.g. ${func1($var_1, $var_3)}
    function_regex_compile = re.compile(r"\$\{([a-zA-Z_]\w*)\(([\$\w\.\-/\s=,]*)\)\}")

    def regex_findall_variables(raw_string: Text) -> List[Text]:
        """extract all variable names from content, which is in format $variable
        Args:
            raw_string (str): string content
        Returns:
            list: variables list extracted from string content
        Examples:
            >>> regex_findall_variables("$variable")
            ["variable"]
            >>> regex_findall_variables("/blog/$postid")
            ["postid"]
            >>> regex_findall_variables("/$var1/$var2")
            ["var1", "var2"]
            >>> regex_findall_variables("abc")
            []
        """
        try:
            match_start_position = raw_string.index("$", 0)
        except ValueError:
            return []

        vars_list = []
        while match_start_position < len(raw_string):

            # Notice: notation priority
            # $$ > $var

            # search $$
            dollar_match = dolloar_regex_compile.match(raw_string, match_start_position)
            if dollar_match:
                match_start_position = dollar_match.end()
                continue

            # search variable like ${var} or $var
            var_match = variable_regex_compile.match(raw_string, match_start_position)
            if var_match:
                var_name = var_match.group(1) or var_match.group(2)
                vars_list.append(var_name)
                match_start_position = var_match.end()
                continue

            curr_position = match_start_position
            try:
                # find next $ location
                match_start_position = raw_string.index("$", curr_position + 1)
            except ValueError:
                # break while loop
                break

        return vars_list

    def extract_variables(content: Any) -> Set:
        """extract all variables in content recursively."""
        if isinstance(content, (list, set, tuple)):
            variables = set()
            for item in content:
                variables = variables | extract_variables(item)
            return variables

        elif isinstance(content, dict):
            variables = set()
            for key, value in content.items():
                variables = variables | extract_variables(value)
            return variables

        elif isinstance(content, str):
            return set(regex_findall_variables(content))

        return set()

    vars = [{'foo1': 'bar1'}, {'foo2': 'bar2'}]
    resp = extract_variables(vars)
    print(resp)

