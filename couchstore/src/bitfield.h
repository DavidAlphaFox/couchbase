#ifndef COUCH_BITFIELD_H
#define COUCH_BITFIELD_H

#include "config.h"
#include "internal.h"
#include <assert.h>
#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Variable-width types. Since these are made out of chars they will be
 * byte-aligned, so structs consisting only of these will be packed.
 */

typedef struct {
    uint8_t raw_bytes[1];
} raw_08;

typedef struct {
    uint8_t raw_bytes[2];
} raw_16;

typedef struct {
    uint8_t raw_bytes[3];
} raw_24;

typedef struct {
    uint8_t raw_bytes[4];
} raw_32;

typedef struct {
    uint8_t raw_bytes[5];
} raw_40;

typedef struct {
    uint8_t raw_bytes[6];
} raw_48;

typedef struct {
    uint8_t raw_bytes[8];
} raw_64;


/* Functions for decoding raw_xx types to native integers: */
#define encode_raw08(a) couchstore_encode_raw08(a)
#define encode_raw16(a) couchstore_encode_raw16(a)
#define encode_raw24(a, b) couchstore_encode_raw24(a, b)
#define encode_raw32(a) couchstore_encode_raw32(a)
#define encode_raw40(a, b) couchstore_encode_raw40(a, b)
#define encode_raw48(a, b) couchstore_encode_raw48(a, b)
#define encode_raw64(a) couchstore_encode_raw64(a)

#define decode_raw08(a) couchstore_decode_raw08(a)
#define decode_raw16(a) couchstore_decode_raw16(a)
#define decode_raw24(a) couchstore_decode_raw24p(&(a))
#define decode_raw32(a) couchstore_decode_raw32(a)
#define decode_raw40(a) couchstore_decode_raw40p(&(a))
#define decode_raw48(a) couchstore_decode_raw48p(&(a))
#define decode_raw64(a) couchstore_decode_raw64(a)

    LIBCOUCHSTORE_API
    uint8_t couchstore_decode_raw08(raw_08 raw);
    LIBCOUCHSTORE_API
    uint16_t couchstore_decode_raw16(raw_16 raw);
    LIBCOUCHSTORE_API
    uint32_t couchstore_decode_raw24p(const raw_24 *raw);
    LIBCOUCHSTORE_API
    uint32_t couchstore_decode_raw32(raw_32 raw);
    LIBCOUCHSTORE_API
    uint64_t couchstore_decode_raw40p(const raw_40 *raw);
    LIBCOUCHSTORE_API
    uint64_t couchstore_decode_raw48p(const raw_48 *raw);
    LIBCOUCHSTORE_API
    uint64_t couchstore_decode_raw64(raw_64 raw);

/* Functions for encoding native integers to raw_xx types: */

    LIBCOUCHSTORE_API
    raw_08 couchstore_encode_raw08(uint8_t value);
    LIBCOUCHSTORE_API
    raw_16 couchstore_encode_raw16(uint16_t value);
    LIBCOUCHSTORE_API
    void couchstore_encode_raw24(uint32_t value, raw_24 *raw);
    LIBCOUCHSTORE_API
    raw_32 couchstore_encode_raw32(uint32_t value);
    LIBCOUCHSTORE_API
    void couchstore_encode_raw40(uint64_t value, raw_40 *raw);
    LIBCOUCHSTORE_API
    void couchstore_encode_raw48(uint64_t value, raw_48 *raw);
    LIBCOUCHSTORE_API
    raw_64 couchstore_encode_raw64(uint64_t value);

#ifdef __cplusplus
}
#endif


#endif
