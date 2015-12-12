/* -*- Mode: C; tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*- */

/**
 * @copyright 2013 Couchbase, Inc.
 *
 * @author Sarath Lakshman  <sarath@couchbase.com>
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy of
 * the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations under
 * the License.
 **/
#include "config.h"
#include "purgers.h"
#include "bitmap.h"
#include "values.h"
#include "reductions.h"
#include "../couch_btree.h"
#include <inttypes.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <inttypes.h>
#include <limits.h>

static int view_purgekv_action(bitmap_t *bm, uint16_t part_id,
                                             uint64_t valcount,
                                             view_purger_ctx_t *ctx)
{
    int action = PURGE_KEEP;
    if (is_bit_set(bm, part_id)) {
        ctx->count += valcount;
        action = PURGE_ITEM;
    }

    return action;
}

static int view_purgekp_action(bitmap_t *clearbm, bitmap_t *redbm,
                                                  uint64_t kvcount,
                                                  view_purger_ctx_t *ctx)
{
    int action = PURGE_PARTIAL;
    bitmap_t emptybm, dstbm = *clearbm;
    memset(&emptybm, 0, sizeof(emptybm));

    if (is_equal_bitmap(redbm, clearbm)) {
        action = PURGE_ITEM;
        ctx->count += kvcount;
    } else {
        intersect_bitmaps(&dstbm, redbm);
        if (is_equal_bitmap(&dstbm, &emptybm)) {
            action = PURGE_KEEP;
        }
    }

    return action;
}

int view_id_btree_purge_kv(const sized_buf *key, const sized_buf *val,
                                                 void *ctx)
{
    int action;
    couchstore_error_t errcode = COUCHSTORE_SUCCESS;
    view_purger_ctx_t *purge_ctx = (view_purger_ctx_t *) ctx;
    view_id_btree_value_t *v = NULL;
    (void) key;

    errcode = decode_view_id_btree_value(val->buf, val->size, &v);
    if (errcode != COUCHSTORE_SUCCESS) {
        action = (int) errcode;
        goto cleanup;
    }

    action = view_purgekv_action(&purge_ctx->cbitmask, v->partition,
                                                       1,
                                                       purge_ctx);

cleanup:
    free_view_id_btree_value(v);
    return action;
}

int view_id_btree_purge_kp(const node_pointer *ptr, void *ctx)
{
    int action;
    couchstore_error_t errcode = COUCHSTORE_SUCCESS;
    view_purger_ctx_t *purge_ctx = (view_purger_ctx_t *) ctx;
    view_id_btree_reduction_t *r = NULL;

    errcode = decode_view_id_btree_reduction(ptr->reduce_value.buf, &r);
    if (errcode != COUCHSTORE_SUCCESS) {
        action = (int) errcode;
        goto cleanup;
    }

    action = view_purgekp_action(&purge_ctx->cbitmask, &r->partitions_bitmap,
                                                       r->kv_count,
                                                       purge_ctx);

cleanup:
    free_view_id_btree_reduction(r);
    return action;
}

int view_btree_purge_kv(const sized_buf *key, const sized_buf *val, void *ctx)
{
    int action;
    couchstore_error_t errcode = COUCHSTORE_SUCCESS;
    view_purger_ctx_t *purge_ctx = (view_purger_ctx_t *) ctx;
    view_btree_value_t *v = NULL;
    (void) key;

    errcode = decode_view_btree_value(val->buf, val->size, &v);
    if (errcode != COUCHSTORE_SUCCESS) {
        action = (int) errcode;
        goto cleanup;
    }

    action = view_purgekv_action(&purge_ctx->cbitmask, v->partition,
                                                       v->num_values,
                                                       purge_ctx);

cleanup:
    free_view_btree_value(v);

    return action;
}

int view_btree_purge_kp(const node_pointer *ptr, void *ctx)
{
    int action;
    couchstore_error_t errcode = COUCHSTORE_SUCCESS;
    view_purger_ctx_t *purge_ctx = (view_purger_ctx_t *) ctx;
    view_btree_reduction_t *r = NULL;

    errcode = decode_view_btree_reduction(ptr->reduce_value.buf,
                                          ptr->reduce_value.size,
                                          &r);
    if (errcode != COUCHSTORE_SUCCESS) {
        action = (int) errcode;
        goto cleanup;
    }

    action = view_purgekp_action(&purge_ctx->cbitmask, &r->partitions_bitmap,
                                                       r->kv_count,
                                                       purge_ctx);

cleanup:
    free_view_btree_reduction(r);
    return action;
}
