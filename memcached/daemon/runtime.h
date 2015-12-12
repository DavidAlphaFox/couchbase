/* -*- Mode: C; tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*- */
/*
*     Copyright 2015 Couchbase, Inc
*
*   Licensed under the Apache License, Version 2.0 (the "License");
*   you may not use this file except in compliance with the License.
*   You may obtain a copy of the License at
*
*       http://www.apache.org/licenses/LICENSE-2.0
*
*   Unless required by applicable law or agreed to in writing, software
*   distributed under the License is distributed on an "AS IS" BASIS,
*   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
*   See the License for the specific language governing permissions and
*   limitations under the License.
*/

/*
 * Due to the fact that the memcached daemon is written in C we need
 * this little wrapper to provide atomics functionality without having
 * to reinvent the wheel
 */
#pragma once

#include <memcached/openssl.h>
#include <memcached/extension.h>

#ifdef __cplusplus
extern "C" {
#endif

    void set_ssl_cipher_list(const char *new_list);
    void set_ssl_ctx_cipher_list(SSL_CTX *ctx, EXTENSION_LOGGER_DESCRIPTOR* logger);

#ifdef __cplusplus
}
#endif
