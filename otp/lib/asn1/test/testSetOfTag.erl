%%
%% %CopyrightBegin%
%%
%% Copyright Ericsson AB 1997-2012. All Rights Reserved.
%%
%% The contents of this file are subject to the Erlang Public License,
%% Version 1.1, (the "License"); you may not use this file except in
%% compliance with the License. You should have received a copy of the
%% Erlang Public License along with this software. If not, it can be
%% retrieved online at http://www.erlang.org/.
%%
%% Software distributed under the License is distributed on an "AS IS"
%% basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See
%% the License for the specific language governing rights and limitations
%% under the License.
%%
%% %CopyrightEnd%
%%
%%
-module(testSetOfTag).
-export([main/1]).

-include_lib("test_server/include/test_server.hrl").
-include("External.hrl").

-record('SetTagNt',{nt}).
-record('SetTagNtI',{imp}).
-record('SetTagNtE',{exp}).
-record('SetTagI',{nt}).
-record('SetTagII',{imp}).
-record('SetTagIE',{exp}).
-record('SetTagE',{nt}).
-record('SetTagEI',{imp}).
-record('SetTagEE',{exp}).
-record('SetTagXNt',{xnt}).
-record('SetTagXI',{ximp}).
-record('SetTagXE',{xexp}).
-record('SetTagImpX',{xnt, ximp, xexp}).
-record('SetTagExpX',{xnt, ximp, xexp}).
-record('NT',{os, bool}).
-record('Imp',{os, bool}).
-record('Exp',{os, bool}).

main(_Rules) ->
    roundtrip('SetTagNt', #'SetTagNt'{nt=[#'NT'{os="kalle",bool=true},
					  #'NT'{os="kalle",bool=true}]}),
    roundtrip('SetTagNtI', #'SetTagNtI'{imp=[#'Imp'{os="kalle",bool=true},
					     #'Imp'{os="kalle",bool=true}]}),
    roundtrip('SetTagNtE', #'SetTagNtE'{exp=[#'Exp'{os="kalle",bool=true},
					     #'Exp'{os="kalle",bool=true}]}),
    roundtrip('SetTagI', #'SetTagI'{nt=[#'NT'{os="kalle",bool=true},
					#'NT'{os="kalle",bool=true}]}),
    roundtrip('SetTagII', #'SetTagII'{imp=[#'Imp'{os="kalle",bool=true},
					   #'Imp'{os="kalle",bool=true}]}),
    roundtrip('SetTagIE', #'SetTagIE'{exp=[#'Exp'{os="kalle",bool=true},
					   #'Exp'{os="kalle",bool=true}]}),
    roundtrip('SetTagE', #'SetTagE'{nt=[#'NT'{os="kalle",bool=true},
					#'NT'{os="kalle",bool=true}]}),
    roundtrip('SetTagEI', #'SetTagEI'{imp=[#'Imp'{os="kalle",bool=true},
					   #'Imp'{os="kalle",bool=true}]}),
    roundtrip('SetTagEE', #'SetTagEE'{exp=[#'Exp'{os="kalle",bool=true},
					   #'Exp'{os="kalle",bool=true}]}),
    roundtrip('SetTagXNt', #'SetTagXNt'{xnt=[#'XSetNT'{os="kalle",bool=true},
					     #'XSetNT'{os="kalle",bool=true}]}),
    roundtrip('SetTagXI', #'SetTagXI'{ximp=[#'XSetImp'{os="kalle",bool=true},
					    #'XSetImp'{os="kalle",bool=true}]}),
    roundtrip('SetTagXE', #'SetTagXE'{xexp=[#'XSetExp'{os="kalle",bool=true},
					    #'XSetExp'{os="kalle",bool=true}]}),
    roundtrip('SetTagImpX', #'SetTagImpX'{xnt=[#'XSetNT'{os="kalle",bool=true},
					       #'XSetNT'{os="kalle",bool=true}],
					  ximp=[#'XSetImp'{os="kalle",bool=true},
						#'XSetImp'{os="kalle",bool=true}],
					  xexp=[#'XSetExp'{os="kalle",bool=true},
						#'XSetExp'{os="kalle",bool=true}]}),
    roundtrip('SetTagExpX', #'SetTagExpX'{xnt=[#'XSetNT'{os="kalle",bool=true},
					       #'XSetNT'{os="kalle",bool=true}],
					  ximp=[#'XSetImp'{os="kalle",bool=true},
						#'XSetImp'{os="kalle",bool=true}],
					  xexp=[#'XSetExp'{os="kalle",bool=true},
						#'XSetExp'{os="kalle",bool=true}]}),
    ok.

roundtrip(T, V) ->
    asn1_test_lib:roundtrip('SetOfTag', T, V).
