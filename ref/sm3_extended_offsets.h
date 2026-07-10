#ifndef SM3_EXTENDED_OFFSETS_H_
#define SM3_EXTENDED_OFFSETS_H_

/*
 * Experimental 26-byte compressed address layout.  The tree field is widened
 * from 8 to 12 bytes; the remaining SM3 fields retain their original shape.
 */

#define SPX_OFFSET_LAYER       0
#define SPX_OFFSET_TREE        1
#define SPX_OFFSET_TYPE        13
#define SPX_OFFSET_KP_ADDR     14
#define SPX_OFFSET_CHAIN_ADDR  21
#define SPX_OFFSET_HASH_ADDR   25
#define SPX_OFFSET_TREE_HGT    21
#define SPX_OFFSET_TREE_INDEX  22

#define SPX_TREE_ADDR_BYTES 12
#define SPX_SM3_ADDR_BYTES 26
#define SPX_SM3 1

#endif
