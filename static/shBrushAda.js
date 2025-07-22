/**
 * SyntaxHighlighter
 * http://alexgorbatchev.com/
 *
 * This brush was originally created by spatterson
 * homepage:   <unknown>
 * brush page: <unknown>
 */
SyntaxHighlighter.brushes.Ada = function()
{
    // Created by Shaun Patterson, shaunpatterson@gmail.com

    var vars = 'integer float long boolean duration string unbounded_string';

    var keywords = 'abort abs abstract accept access aliased all and array at ' +
                   'begin body case constant declare delay delta digits do else ' +
                   'elsif end entry exception exit for function generic goto if ' +
                   'in interface is limited loop mod new not null of or ' +
                   'others out overriding package pragma private procedure protected ' +
                   'raise range record rem renames requeue return reverse ' +
                   'select separate subtype synchronized tagged task terminate ' +
                   'then type until use when while with xor ';

    var attributes = 'access address adjacent aft alignment base bit_order body_version ' +
                     'callable caller ceiling class component_size compose constrained ' +
                     'copy_sign count definite delta denom digits emax exponent external_tag ' +
                     'epsilon first first_bit floor fore fraction identity image img input ' +
                     'large last last_bit leading_part length machine machine_emax machine_emin ' +
                     'machine_mantissa machine_overflows machine_radix machine_rounding ' +
                     'machine_rounds mantissa max max_size_in_storage_elements min mod ' +
                     'modle model_emin model_epsilon model_mantissa model_small modulus ' +
                     'output partition_id pos position pred priority range read remainder ' +
                     'round rounding safe_emax safe_first safe_large safe_last safe_small ' + 
                     'scale scaling signed_zeros size small storage_pool storage_size ' +
                     'stream_size succ tag terminated truncation unbaised_rounding ' + 
                     'unchecked_access val valid value version wide_image wide_value ' + 
                     'wide_wide_image wide_wide_value wide_wide_width wide_width width write ';


    this.regexList = [
        { regex: new RegExp('--.*$', 'gm'),                                 css: 'comments' },     // -- comment string
        { regex: /\b([\d]+(\.[\d]+)?|0x[a-f0-9]+)\b/gi,                     css: 'value' },        // numbers
        { regex: new RegExp(this.getKeywords(keywords), 'gmi'),             css: 'keyword' },      // keywords
        { regex: new RegExp(this.getKeywords(vars), 'gmi'),                 css: 'variable' },     // variable
        { regex: new RegExp("'" + this.getKeywords(attributes), 'gmi'),     css: 'variable' },     // attributes
    ];
    
    this.forHtmlScript(SyntaxHighlighter.regexLib.scriptScriptTags);
};

SyntaxHighlighter.brushes.Ada.prototype    = new SyntaxHighlighter.Highlighter();
SyntaxHighlighter.brushes.Ada.aliases    = ['ada'];
/*
     FILE ARCHIVED ON 15:18:09 Aug 08, 2011 AND RETRIEVED FROM THE
     INTERNET ARCHIVE ON 13:45:54 Nov 08, 2019.
     JAVASCRIPT APPENDED BY WAYBACK MACHINE, COPYRIGHT INTERNET ARCHIVE.

     ALL OTHER CONTENT MAY ALSO BE PROTECTED BY COPYRIGHT (17 U.S.C.
     SECTION 108(a)(3)).
*/
/*
playback timings (ms):
  PetaboxLoader3.datanode: 46.762 (4)
  exclusion.robots.policy: 0.161
  captures_list: 145.998
  load_resource: 82.095
  RedisCDXSource: 2.58
  exclusion.robots: 0.175
  PetaboxLoader3.resolve: 136.356 (2)
  CDXLines.iter: 15.134 (3)
  LoadShardBlock: 124.982 (3)
  esindex: 0.033
*/
