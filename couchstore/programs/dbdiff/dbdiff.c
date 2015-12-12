/* -*- Mode: C; tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*- */
#include "config.h"
#include <getopt.h>
#include <ctype.h>

#include <string.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <libcouchstore/couch_db.h>

static int quiet = 0;
struct compare_context {
    Db *this;
    DbInfo this_info;
    Db *other;
    DbInfo other_info;
    int diff;
};

static void usage(void) {
    fprintf(stderr, "USAGE: dbdiff [-q] file1 file2\n");
    fprintf(stderr, "   -q\tquiet\n");
    exit(EXIT_FAILURE);
}

static int is_printable_key(const uint8_t *data, size_t size) {
    size_t ii;
    for (ii = 0; ii < size; ++ii) {
        if (!isprint(data[ii])) {
            return 0;
        }
    }

    return 1;
}

static void print_key(const void *data, size_t size) {
    if (is_printable_key(data, size)) {
        fwrite(data, 1, size, stderr);
    } else {
        size_t ii;
        for (ii = 0; ii < size; ++ii) {
            fprintf(stderr, "0x%02x", ((uint8_t*)data)[ii]);
        }
    }
}

static void print_missing(const uint8_t *data, size_t size, const char *fname) {
    if (!quiet) {
        fprintf(stderr, "Document \"");
        print_key(data, size);
        fprintf(stderr, "\" is missing from \"%s\"\n", fname);
    }
}

static void compare_docinfo(struct compare_context *ctx, DocInfo *a, DocInfo *b) {
    if (a->db_seq != b->db_seq) {
        if (!quiet) {
            fprintf(stderr, "Document db_seq differs for \"");
            print_key(a->id.buf, a->id.size);
            fprintf(stderr, "\": %" PRIu64 " - %" PRIu64 "\n",
                    a->db_seq, b->db_seq);
            ctx->diff = 1;
        }
    }

    if (a->rev_seq != b->rev_seq) {
        if (!quiet) {
            fprintf(stderr, "Document rev_seq differs for \"");
            print_key(a->id.buf, a->id.size);
            fprintf(stderr, "\": %" PRIu64 " - %" PRIu64 "\n",
                    a->rev_seq, b->rev_seq);
            ctx->diff = 1;
        }
    }

    if (a->rev_meta.size != b->rev_meta.size) {
        if (!quiet) {
            fprintf(stderr, "Document rev_meta size differs for \"");
            print_key(a->id.buf, a->id.size);
            fprintf(stderr, "\": %" PRIu64 " - %" PRIu64 "\n",
                    (uint64_t)a->rev_meta.size, (uint64_t)b->rev_meta.size);
            fprintf(stderr, "\"\n");
            ctx->diff = 1;
        }
    } else if (memcmp(a->rev_meta.buf, b->rev_meta.buf, a->rev_meta.size) != 0) {
        if (!quiet) {
            fprintf(stderr, "Document rev_meta differs for \"");
            print_key(a->id.buf, a->id.size);
            fprintf(stderr, "\"\n");
            ctx->diff = 1;
        }
    }

    if (a->deleted != b->deleted) {
        if (!quiet) {
            fprintf(stderr, "Document deleted status differs for \"");
            print_key(a->id.buf, a->id.size);
            fprintf(stderr, "\": %u - %u\n", a->deleted, b->deleted);
            ctx->diff = 1;
        }
    }

    if (a->content_meta != b->content_meta) {
        if (!quiet) {
            fprintf(stderr, "Document content_meta differs for \"");
            print_key(a->id.buf, a->id.size);
            fprintf(stderr, "\": %02x - %02x\n", a->content_meta,
                    b->content_meta);
            ctx->diff = 1;
        }
    }

    if (a->size != b->size) {
        if (!quiet) {
            fprintf(stderr, "Document size differs for \"");
            print_key(a->id.buf, a->id.size);
            fprintf(stderr, "\": %" PRIu64 " - %" PRIu64 "\n",
                    (uint64_t)a->size, (uint64_t)b->size);
            ctx->diff = 1;
        }
    }
}

static void compare_documents(struct compare_context *ctx,
                              DocInfo *this_doc_info,
                              DocInfo *other_doc_info)
{
    couchstore_error_t e1, e2;
    Doc *d1, *d2;

    if (this_doc_info->deleted) {
        return ;
    }

    e1 = couchstore_open_document(ctx->this, this_doc_info->id.buf,
                                  this_doc_info->id.size, &d1, 0);
    e2 = couchstore_open_document(ctx->other, other_doc_info->id.buf,
                                  other_doc_info->id.size, &d2, 0);

    if (e1 == COUCHSTORE_SUCCESS && e2 == COUCHSTORE_SUCCESS) {
        if (d1->data.size != d2->data.size) {
            ctx->diff = 1;
            if (!quiet) {
                fprintf(stderr, "Document \"");
                print_key(this_doc_info->id.buf, this_doc_info->id.size);
                fprintf(stderr, "\" differs in size!\n");

            }
        } else if (memcmp(d1->data.buf, d2->data.buf, d1->data.size) != 0) {
            ctx->diff = 1;
            if (!quiet) {
                fprintf(stderr, "Document \"");
                print_key(this_doc_info->id.buf, this_doc_info->id.size);
                fprintf(stderr, "\" content differs!\n");
            }
        }
        couchstore_free_document(d1);
        couchstore_free_document(d2);
    } else {
        fprintf(stderr, "Failed to open document from this\n this: %s\n other: %s\n",
                couchstore_strerror(e1),
                couchstore_strerror(e2));
        exit(EXIT_FAILURE);
    }
}

static int deep_compare(Db *db, DocInfo *docinfo, void *c) {
    struct compare_context *ctx = c;
    DocInfo *other_doc_info;
    couchstore_error_t err;

    err = couchstore_docinfo_by_id(ctx->other,
                                   docinfo->id.buf,
                                   docinfo->id.size,
                                   &other_doc_info);

    if (err == COUCHSTORE_SUCCESS) {
        /* verify that the docinfos are the same.. */
        compare_docinfo(ctx, docinfo, other_doc_info);
        compare_documents(ctx, docinfo, other_doc_info);
        couchstore_free_docinfo(other_doc_info);
    } else {
        ctx->diff = 1;
        print_missing((void*)docinfo->id.buf,
                      docinfo->id.size,
                      ctx->other_info.filename);
    }

    return 0;
}

static int check_existing(Db *db, DocInfo *docinfo, void *c) {
    struct compare_context *ctx = c;
    couchstore_error_t err;
    Doc *doc;

    err = couchstore_open_document(ctx->other,
                                   docinfo->id.buf,
                                   docinfo->id.size,
                                   &doc, 0);
    if (err == COUCHSTORE_SUCCESS) {
        couchstore_free_document(doc);
    } else if (err == COUCHSTORE_ERROR_DOC_NOT_FOUND) {
        ctx->diff = 1;
        print_missing((void*)docinfo->id.buf,
                      docinfo->id.size,
                      ctx->other_info.filename);
    } else {
        fprintf(stderr, "Error trying to read \"");
        print_key(docinfo->id.buf, docinfo->id.size);
        fprintf(stderr, "\" from \"%s\": %s\n",
                ctx->other_info.filename, couchstore_strerror(err));
        exit(EXIT_FAILURE);
    }

    return 0;
}

static int diff(Db **dbs) {
    couchstore_error_t err;
    struct compare_context ctx;
    DbInfo info;

    ctx.diff = 0;
    ctx.this = dbs[0];
    ctx.other = dbs[1];

    if (couchstore_db_info(ctx.this, &ctx.this_info) != COUCHSTORE_SUCCESS ||
        couchstore_db_info(ctx.other, &ctx.other_info) != COUCHSTORE_SUCCESS) {
        fprintf(stderr, "Failed to get database info..\n");
        exit(EXIT_FAILURE);
    }

    err = couchstore_all_docs(ctx.this, NULL, 0, deep_compare, &ctx);
    if (err != COUCHSTORE_SUCCESS) {
        fprintf(stderr, "An error occured: %s\n",
                couchstore_strerror(err));
        return -1;
    }

    ctx.this = dbs[1];
    ctx.other = dbs[0];
    info = ctx.this_info;
    ctx.this_info = ctx.other_info;
    ctx.other_info = info;

    err = couchstore_all_docs(ctx.this, NULL, 0, check_existing, &ctx);
    if (err != COUCHSTORE_SUCCESS) {
        fprintf(stderr, "An error occured: %s\n",
                couchstore_strerror(err));
        return -1;
    }

    return ctx.diff;
}

int main(int argc, char **argv)
{
    int cmd;
    int ii;
    Db *dbs[2];
    int difference;

    while ((cmd = getopt(argc, argv, "q")) != -1) {
        switch (cmd) {
        case 'q':
            quiet = 1;
            break;

        default:
            usage();
            /* NOT REACHED */
        }
    }

    if ((optind + 2) != argc) {
        fprintf(stderr, "Exactly two filenames should be specified\n");
        usage();
        /* NOT REACHED */
    }

    for (ii = 0; ii < 2; ++ii) {
        couchstore_error_t err;
        err = couchstore_open_db(argv[optind + ii],
                                 COUCHSTORE_OPEN_FLAG_RDONLY,
                                 &dbs[ii]);
        if (err != COUCHSTORE_SUCCESS) {
            fprintf(stderr, "Failed to open \"%s\": %s\n",
                    argv[optind + ii], couchstore_strerror(err));
            if (ii == 1) {
                couchstore_close_db(dbs[0]);
            }
            exit(EXIT_FAILURE);
        }
    }

    difference = diff(dbs);
    for (ii = 0; ii < 2; ++ii) {
        couchstore_close_db(dbs[ii]);
    }

    if (difference == 0) {
        if (!quiet) {
            fprintf(stdout, "The content of the databases is the same\n");
        }
        return EXIT_SUCCESS;
    }

    return EXIT_FAILURE;
}
