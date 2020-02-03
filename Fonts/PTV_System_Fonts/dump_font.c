
#if DUMP_SYSTEM_FONTS

////////////////////////////////////////////////////////////
// each glyph in the font file starts with a standard header
//
// Glyph data is 1 bit per pixel for regular fonts, and
// 4 bits (one nibble) per pixel for AA fonts.
//
// Numbers and bit data is packed "big endian".
// E.g., bits are numbered 0..7, as follows:

#define GET_BIT( BYTE, BITNUM ) ( 0x1 & (( BYTE ) >> ( 7 - ( BITNUM ))))

typedef struct {
    ui16    code;       // the character code (redundant)
    ui16    yoff;       // y offset of bitmap (bitmap starts this many rows down)
    ui16    advance;    // amount to advance origin along baseline after drawing glyph
    ui16    height;     // overall height of this bitmap (
    ui16    xoff;       // x offset of bitmap (starts this many columns to the right)
    ui16    width;      // width of bitmap
    ui8     data[ 0 ];  // bitmap data (may include 1 or 2 trailing bytes that are partially used or not at all)
} PTVFontGlyphHeader;

// how to compute data bytes (non-AA only)

#define NUM_GLYPH_DATA_BYTES( HEADER )      \
    (((( HEADER )->width * ( HEADER )->height ) / 8 ) + 1 )

////////////////////////////////////////////////////////////
// each font file starts with this header

typedef struct {
    char    magic[ 4 ];     // "PTVF"
    ui32    version;        // font version
    ui32    unk1;           // 0=> 1 bit fonts; 4=> 4 bit/AA
    ui16    count;          // code for "max" glyph 
                            // (i.e., the largest one NOT in the file)
                            // (e.g., 0x100 for 0..127)
    ui16    unk2;           // ?? width of space??
    ui16    fontSize;       // font size in points
    ui16    ascent;         // position of baseline from top of font
    ui32    glyphs[ 0 ];    // array[count] of OFFSETS (relative to FontFileHeader) 
                            // to each individual PTVFontGlyphHeader;
                            // 0xFFFFFFFF signifies missing glyphs in the range 0..max
} PTVFontFileHeader;


////////////////////////////////////////////////////////////
// structure internal to PTV

typedef struct {
    ui16    unk1;
    ui16    fontSize;
    ui16    unk2;
    ui16    unk3;
    ui16    unk4;
    ui16    unk5;
    ui32    version;
    PTVFontGlyphHeader*     glyphBase;
    PTVFontFileHeader*      fontFileHeader;
    char    data[ 0x168 - 24 ];    // about this much more unknown gunk
} PTVSysFontData;


////////////////////////////////////////////////////////
// function to dump font data from ROM

void GfxText_DumpFont( Pd_FontStyleID font, const char* filename )
{
    PTVSysFontData* fontData = (PTVSysFontData*)pd_GetFontAttribute( font, kPd_FontData, 0 );
    PTVFontFileHeader* fontFile = fontData->fontFileHeader;
    char buf[666];
    Strm_ID sid;
    ui32 len = 0;
    int i;
    
    /////////////////////////
    // create a *.txt file with generic info via pd_GetFontAttribute()
    
    strcpy( buf, "file://" );
    strcat( buf, filename );
    strcat( buf, ".txt" );
    sid = strm_Open( buf, kStrm_Truncate, NULL );

#define SHOW( WHAT, FMT, TYPE )                         \
    sprintf( buf, "Font.%s.%s: " FMT, filename, #WHAT,  \
        (TYPE)pd_GetFontAttribute( font, WHAT, 0 ));    \
    ERR_N( "%s", buf );                                 \
    strcat( buf, "\r\n" );                              \
    strm_Write( sid, buf, strlen( buf ), NULL );


    SHOW( kPd_AntiAliasing, "%8x", ui32 );
    SHOW( kPd_BackShadow, "%8x", ui32 );
    SHOW( kPd_CustomAttribute, "%8x", ui32 );
    SHOW( kPd_DropShadow, "%8x", ui32 );
    SHOW( kPd_EncodingScheme, "%8x", ui32 );
    SHOW( kPd_FontData, "%8x", ui32 );
    SHOW( kPd_FontVersion, "%8x", ui32 );
    SHOW( kPd_Mapping, "%8x", ui32 );
    SHOW( kPd_NonPrintingCharacter, "%8x", ui32 );
    SHOW( kPd_Pitch, "%d", ui32 );
    SHOW( kPd_PointSize, "%d", ui32 );
    SHOW( kPd_Rotation, "%d", ui32 );
    SHOW( kPd_SharedDataSize, "%d", ui32 );
    SHOW( kPd_Tracking, "%8x", ui32 );
    SHOW( kPd_Translucency, "%8x", ui32 );
    SHOW( kPd_Typeface, "%8x", ui32 );
    SHOW( kPd_UnderlineThickness, "%d", ui32 );
    SHOW( kPd_Weight, "%d", ui32 );
    SHOW( kPd_Width, "%d", ui32 );    
#undef SHOW

    strm_Close( sid );
    
    ///////////////////////////////
    // figure out end of font data region
    //
    //  Staring with last glyph, find first one != FFFFFFFF.
    //  Total size is its offset plus 0x100 (hopefully with some extra bytes).
    
    for( i = fontFile->count - 1; i > 0; i-- ){
        ui32 offset = fontFile->glyphs[ i ];
        if( offset != 0xFFFFFFFF ){
            len = offset + 0x100;
            printf( "%d glyphs, last=%d, off=%d, %d bytes written\n", fontFile->count, i, offset, len );
            break;
        }
    }
    
    ///////////////////////////////
    // write font file in proprietary ".bft" format.
    //

    if( len ){    
        strcpy( buf, "file://" );
        strcat( buf, filename );
        strcat( buf, ".bft" );
        sid = strm_Open( buf, kStrm_Truncate, NULL );
        strm_Write( sid, fontFile, len, NULL );
        strm_Close( sid );
    } else {
        printf( "!! Cannot figure out length of font file!!\n" );
    }
}
#endif // DUMP_SYSTEM_FONTS