#ifndef SM3_OFFSETS_H_
#define SM3_OFFSETS_H_

/*
 * SM3 uses the same 22-byte compressed address layout as the SHA-2 backend.
 */

#define SPX_OFFSET_LAYER     0
#define SPX_OFFSET_TREE      1
#define SPX_OFFSET_TYPE      9
#define SPX_OFFSET_KP_ADDR   10
#define SPX_OFFSET_CHAIN_ADDR 17
#define SPX_OFFSET_HASH_ADDR 21
#define SPX_OFFSET_TREE_HGT  17
#define SPX_OFFSET_TREE_INDEX 18

#define SPX_TREE_ADDR_BYTES 8

#define SPX_SM3 1

#endif
