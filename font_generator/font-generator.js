const fs = require('fs');
const path = require('path');

const svgicons2svgfont = require('svgicons2svgfont');
const svg2ttf = require('svg2ttf');

const fontName = 'sheikah';
const fontVersion = '1.0';
const fontStream = svgicons2svgfont({
  fontName: fontName,
  descent: 200
});

const inputSettings = [
  {
    svgDirectory: '../output/w110_n180/round',
    charMetadata: [
      { name: '0', svgPath: '0.svg' },
      { name: '1', svgPath: '1.svg' },
      { name: '2', svgPath: '2.svg' },
      { name: '3', svgPath: '3.svg' },
      { name: '4', svgPath: '4.svg' },
      { name: '5', svgPath: '5.svg' },
      { name: '6', svgPath: '6.svg' },
      { name: '7', svgPath: '7.svg' },
      { name: '8', svgPath: '8.svg' },
      { name: '9', svgPath: '9.svg' }
    ]
  },
  {
    svgDirectory: '../output/w150_n100/rounded-bevel',
    charMetadata: [
      { name: 'A', svgPath: 'a.svg' },
      { name: 'B', svgPath: 'b.svg' },
      { name: 'C', svgPath: 'c.svg' },
      { name: 'D', svgPath: 'd.svg' },
      { name: 'E', svgPath: 'e.svg' },
      { name: 'F', svgPath: 'f.svg' },
      { name: 'G', svgPath: 'g.svg' },
      { name: 'H', svgPath: 'h.svg' },
      { name: 'I', svgPath: 'i.svg' },
      { name: 'J', svgPath: 'j.svg' },
      { name: 'K', svgPath: 'k.svg' },
      { name: 'L', svgPath: 'l.svg' },
      { name: 'M', svgPath: 'm.svg' },
      { name: 'N', svgPath: 'n.svg' },
      { name: 'O', svgPath: 'o.svg' },
      { name: 'P', svgPath: 'p.svg' },
      { name: 'Q', svgPath: 'q.svg' },
      { name: 'R', svgPath: 'r.svg' },
      { name: 'S', svgPath: 's.svg' },
      { name: 'T', svgPath: 't.svg' },
      { name: 'U', svgPath: 'u.svg' },
      { name: 'V', svgPath: 'v.svg' },
      { name: 'W', svgPath: 'w.svg' },
      { name: 'X', svgPath: 'x.svg' },
      { name: 'Y', svgPath: 'y.svg' },
      { name: 'Z', svgPath: 'z.svg' }
    ]
  },
  {
    svgDirectory: '../output/w180_n45/round',
    charMetadata: [
      { name: ' ', svgPath: 'SPACE.svg' },
      { name: '.', svgPath: 'FULL_STOP.svg' },
      { name: 'a', svgPath: 'a.svg' },
      { name: 'b', svgPath: 'b.svg' },
      { name: 'c', svgPath: 'c.svg' },
      { name: 'd', svgPath: 'd.svg' },
      { name: 'e', svgPath: 'e.svg' },
      { name: 'f', svgPath: 'f.svg' },
      { name: 'g', svgPath: 'g.svg' },
      { name: 'h', svgPath: 'h.svg' },
      { name: 'i', svgPath: 'i.svg' },
      { name: 'j', svgPath: 'j.svg' },
      { name: 'k', svgPath: 'k.svg' },
      { name: 'l', svgPath: 'l.svg' },
      { name: 'm', svgPath: 'm.svg' },
      { name: 'n', svgPath: 'n.svg' },
      { name: 'o', svgPath: 'o.svg' },
      { name: 'p', svgPath: 'p.svg' },
      { name: 'q', svgPath: 'q.svg' },
      { name: 'r', svgPath: 'r.svg' },
      { name: 's', svgPath: 's.svg' },
      { name: 't', svgPath: 't.svg' },
      { name: 'u', svgPath: 'u.svg' },
      { name: 'v', svgPath: 'v.svg' },
      { name: 'w', svgPath: 'w.svg' },
      { name: 'x', svgPath: 'x.svg' },
      { name: 'y', svgPath: 'y.svg' },
      { name: 'z', svgPath: 'z.svg' }
    ]
  }
];

const tmpSvgFontPath = 'dest/tmp.svg';
const destinationPath = `dest/${fontName}.ttf`;

// Setting the svg font destination
fontStream.pipe(fs.createWriteStream(tmpSvgFontPath))
  .on('finish', () => {
    console.log('SVG Font successfully created!');

    // Create ttf font
    const ttf = svg2ttf(fs.readFileSync(tmpSvgFontPath).toString(), {version: fontVersion});
    fs.writeFileSync(destinationPath, new Buffer(ttf.buffer));
  })
  .on('error', (err) => {
    console.log(err);
  });

// Writing glyphs
const loadInputSetting = (inputSetting) => {
  const svgDirectory = inputSetting.svgDirectory;

  inputSetting.charMetadata.forEach((metadata) => {
    const svgPath = path.join(svgDirectory, metadata.svgPath);
    const glyph = fs.createReadStream(svgPath);
    glyph.metadata = {
      name: metadata.name,
      unicode: [metadata.name]
    };
    fontStream.write(glyph);
  });
};

inputSettings.forEach(loadInputSetting);

// End the stream
fontStream.end();
