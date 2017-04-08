const svgicons2svgfont = require('svgicons2svgfont');
const fs = require('fs');
const fontStream = svgicons2svgfont({
  fontName: 'sheikah'
});

const data = [
  { name: '0', unicode: ['\u0030'] },
  { name: '1', unicode: ['\u0031'] },
  { name: '2', unicode: ['\u0032'] },
  { name: '3', unicode: ['\u0033'] },
  { name: '4', unicode: ['\u0034'] },
  { name: '5', unicode: ['\u0035'] },
  { name: '6', unicode: ['\u0036'] },
  { name: '7', unicode: ['\u0037'] },
  { name: '8', unicode: ['\u0038'] },
  { name: '9', unicode: ['\u0039'] },
  { name: 'A', unicode: ['\u0041', '\u0061'] },
  { name: 'B', unicode: ['\u0042', '\u0062'] },
  { name: 'C', unicode: ['\u0043', '\u0063'] },
  { name: 'D', unicode: ['\u0044', '\u0064'] },
  { name: 'E', unicode: ['\u0045', '\u0065'] },
  { name: 'F', unicode: ['\u0046', '\u0066'] },
  { name: 'G', unicode: ['\u0047', '\u0067'] },
  { name: 'H', unicode: ['\u0048', '\u0068'] },
  { name: 'I', unicode: ['\u0049', '\u0069'] },
  { name: 'J', unicode: ['\u004A', '\u006A'] },
  { name: 'K', unicode: ['\u004B', '\u006B'] },
  { name: 'L', unicode: ['\u004C', '\u006C'] },
  { name: 'M', unicode: ['\u004D', '\u006D'] },
  { name: 'N', unicode: ['\u004E', '\u006E'] },
  { name: 'O', unicode: ['\u004F', '\u006F'] },
  { name: 'P', unicode: ['\u0050', '\u0070'] },
  { name: 'Q', unicode: ['\u0051', '\u0071'] },
  { name: 'R', unicode: ['\u0052', '\u0072'] },
  { name: 'S', unicode: ['\u0053', '\u0073'] },
  { name: 'T', unicode: ['\u0054', '\u0074'] },
  { name: 'U', unicode: ['\u0055', '\u0075'] },
  { name: 'V', unicode: ['\u0056', '\u0076'] },
  { name: 'W', unicode: ['\u0057', '\u0077'] },
  { name: 'X', unicode: ['\u0058', '\u0078'] },
  { name: 'Y', unicode: ['\u0059', '\u0079'] },
  { name: 'Z', unicode: ['\u005A', '\u007A'] },
];

const svgIconsPath = '../glyph/output/w150_n100';
const destinationPath = 'dest/sheikah.svg';

// Setting the font destination
fontStream.pipe(fs.createWriteStream(destinationPath))
  .on('finish', () => {
    console.log('Font successfully created!')
  })
  .on('error', (err) => {
    console.log(err);
  });

// Writing glyphs
data.forEach((d) => {
  const glyph = fs.createReadStream(`${svgIconsPath}/${d.name.toLowerCase()}.svg`);
  glyph.metadata = {
    name: d.name,
    unicode: d.unicode
  };
  fontStream.write(glyph);
});

// Do not forget to end the stream
fontStream.end();
