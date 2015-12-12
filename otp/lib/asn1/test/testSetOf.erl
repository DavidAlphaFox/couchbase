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
-module(testSetOf).

-export([main/1]).

-include_lib("test_server/include/test_server.hrl").

-record('Set1',{bool1, int1, set1 = asn1_DEFAULT}).
-record('Set2',{set2 = asn1_DEFAULT, bool2, int2}).
-record('Set3',{bool3, set3 = asn1_DEFAULT, int3}).
-record('Set4',{set41 = asn1_DEFAULT, set42 = asn1_DEFAULT, set43 = asn1_DEFAULT}).
-record('SetIn',{boolIn, intIn}).
-record('SetEmp',{set1}).
-record('Empty',{}).



main(_Rules) ->
    roundtrip('Set1',
	      #'Set1'{bool1=true,int1=17,set1=asn1_DEFAULT},
	      #'Set1'{bool1=true,int1=17,set1=[]}),
    roundtrip('Set1',
	      #'Set1'{bool1=true,int1=17,
		      set1=[#'SetIn'{boolIn=true,intIn=25}]}),
    roundtrip('Set1', #'Set1'{bool1=true,int1=17,
			      set1=[#'SetIn'{boolIn=true,intIn=25},
				    #'SetIn'{boolIn=false,intIn=125},
				    #'SetIn'{boolIn=false,intIn=225}]}),

    roundtrip('Set2',
	      #'Set2'{set2=asn1_DEFAULT,bool2=true,int2=17},
	      #'Set2'{set2=[],bool2=true,int2=17}),
    roundtrip('Set2',
	      #'Set2'{set2=[#'SetIn'{boolIn=true,intIn=25}],
		      bool2=true,int2=17}),
    roundtrip('Set2',
	      #'Set2'{set2=[#'SetIn'{boolIn=true,intIn=25},
			    #'SetIn'{boolIn=false,intIn=125},
			    #'SetIn'{boolIn=false,intIn=225}],
		      bool2=true,int2=17}),

    roundtrip('Set3',
	      #'Set3'{bool3=true,set3=asn1_DEFAULT,int3=17},
	      #'Set3'{bool3=true,set3=[],int3=17}),
    roundtrip('Set3',
	      #'Set3'{bool3=true,set3=[#'SetIn'{boolIn=true,intIn=25}],
		      int3=17}),
    roundtrip('Set3',
	      #'Set3'{bool3=true,
		      set3=[#'SetIn'{boolIn=true,intIn=25},
			    #'SetIn'{boolIn=false,intIn=125},
			    #'SetIn'{boolIn=false,intIn=225}],
		      int3=17}),

    roundtrip('Set4',
	      #'Set4'{set41=asn1_DEFAULT,set42=asn1_DEFAULT,
		      set43=asn1_DEFAULT},
	      #'Set4'{set41=[],set42=[],set43=[]}),
    roundtrip('Set4',
	      #'Set4'{set41=[#'SetIn'{boolIn=true,intIn=25}],
		      set42=asn1_DEFAULT,set43=asn1_DEFAULT},
	      #'Set4'{set41=[#'SetIn'{boolIn=true,intIn=25}],
		      set42=[],set43=[]}),
    roundtrip('Set4',
	      #'Set4'{set41=[#'SetIn'{boolIn=true,intIn=25},
			     #'SetIn'{boolIn=false,intIn=125},
			     #'SetIn'{boolIn=false,intIn=225}],
		      set42=asn1_DEFAULT,set43=asn1_DEFAULT},
	      #'Set4'{set41=[#'SetIn'{boolIn=true,intIn=25},
			     #'SetIn'{boolIn=false,intIn=125},
			     #'SetIn'{boolIn=false,intIn=225}],
		      set42=[],set43=[]}),
    roundtrip('Set4',
	      #'Set4'{set41=asn1_DEFAULT,
		      set42=[#'SetIn'{boolIn=true,intIn=25}],
		      set43=asn1_DEFAULT},
	      #'Set4'{set41=[],
		      set42=[#'SetIn'{boolIn=true,intIn=25}],
		      set43=[]}),
    roundtrip('Set4',
	      #'Set4'{set41=asn1_DEFAULT,
		      set42=[#'SetIn'{boolIn=true,intIn=25},
			     #'SetIn'{boolIn=false,intIn=125},
			     #'SetIn'{boolIn=false,intIn=225}],
		      set43=asn1_DEFAULT},
	      #'Set4'{set41=[],
		      set42=[#'SetIn'{boolIn=true,intIn=25},
			     #'SetIn'{boolIn=false,intIn=125},
			     #'SetIn'{boolIn=false,intIn=225}],
		      set43=[]}),
    roundtrip('Set4',
	      #'Set4'{set41=asn1_DEFAULT,set42=asn1_DEFAULT,
		      set43=[#'SetIn'{boolIn=true,intIn=25}]},
	      #'Set4'{set41=[],set42=[],
		      set43=[#'SetIn'{boolIn=true,intIn=25}]}),
    roundtrip('Set4',
	      #'Set4'{set41=asn1_DEFAULT,set42=asn1_DEFAULT,
		      set43=[#'SetIn'{boolIn=true,intIn=25},
			     #'SetIn'{boolIn=false,intIn=125},
			     #'SetIn'{boolIn=false,intIn=225}]},
	      #'Set4'{set41=[],set42=[],
		      set43=[#'SetIn'{boolIn=true,intIn=25},
			     #'SetIn'{boolIn=false,intIn=125},
			     #'SetIn'{boolIn=false,intIn=225}]}),

    roundtrip('SetOs', ["First","Second","Third"]),
    roundtrip('SetOsImp', ["First","Second","Third"]),
    roundtrip('SetOsExp', ["First","Second","Third"]),
    roundtrip('SetEmp', #'SetEmp'{set1=[#'Empty'{}]}),

    ok.

roundtrip(T, V) ->
    roundtrip(T, V, V).

roundtrip(Type, Value, ExpectedValue) ->
    asn1_test_lib:roundtrip('SetOf', Type, Value, ExpectedValue).
