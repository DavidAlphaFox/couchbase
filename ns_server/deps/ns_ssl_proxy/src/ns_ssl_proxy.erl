%% @author Couchbase <info@couchbase.com>
%% @copyright 2013 Couchbase, Inc.
%%
%% Licensed under the Apache License, Version 2.0 (the "License");
%% you may not use this file except in compliance with the License.
%% You may obtain a copy of the License at
%%
%%      http://www.apache.org/licenses/LICENSE-2.0
%%
%% Unless required by applicable law or agreed to in writing, software
%% distributed under the License is distributed on an "AS IS" BASIS,
%% WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
%% See the License for the specific language governing permissions and
%% limitations under the License.

-module(ns_ssl_proxy).

-behaviour(application).

%% Application callbacks
-export([start/2, stop/1]).

%% child_erlang callbacks
-export([start/0, stop/0]).

-include("ns_common.hrl").
-include_lib("ale/include/ale.hrl").

%% ===================================================================
%% Application callbacks
%% ===================================================================

start() ->
    application:start(ns_ssl_proxy, permanent).

start(_StartType, _StartArgs) ->
    application:start(ale),
    application:start(inet),
    ssl:start(permanent),
    setup_env(),
    init_logging(),
    ns_ssl_proxy_sup:start_link().

stop(_State) ->
    ok.

%% called by child_erlang when we're asked to exit. For ssl proxy we
%% can just exit without stopping anything
stop() ->
    ok.

setup_env() ->
    EnvArgsStr = os:getenv("NS_SSL_PROXY_ENV_ARGS"),
    true = is_list(EnvArgsStr),

    {ok, EnvArgs} = couch_util:parse_term(EnvArgsStr),
    lists:foreach(
      fun ({Key, Value}) ->
              application:set_env(ns_ssl_proxy, Key, Value)
      end, EnvArgs).

init_logging() ->
    {ok, Dir} = application:get_env(ns_ssl_proxy, error_logger_mf_dir),
    DiskSinkOpts = misc:get_env_default(ns_ssl_proxy, disk_sink_opts, []),

    LogPath = filename:join(Dir, ?SSL_PROXY_LOG_FILENAME),

    ok = ale:start_sink(ssl_proxy_sink,
                        ale_disk_sink, [LogPath, DiskSinkOpts]),

    ok = ale:start_logger(?NS_SERVER_LOGGER, debug),
    ok = ale:set_loglevel(?ERROR_LOGGER, debug),

    ok = ale:add_sink(?NS_SERVER_LOGGER, ssl_proxy_sink, debug),
    ok = ale:add_sink(?ERROR_LOGGER, ssl_proxy_sink, debug),

    case misc:get_env_default(ns_ssl_proxy, dont_suppress_stderr_logger, false) of
        true ->
            ale:stop_sink(stderr),
            ok = ale:start_sink(stderr, ale_stderr_sink, []),

            lists:foreach(
              fun (Logger) ->
                      ok = ale:add_sink(Logger, stderr, debug)
              end, [?NS_SERVER_LOGGER, ?ERROR_LOGGER]);
        false ->
            ok
    end,
    ale:info(?NS_SERVER_LOGGER, "Brought up ns_ssl_proxy logging").
