const svgicons2svgfont = require('svgicons2svgfont');
const fs = require('fs');
const path = require('path');
const fontStream = svgicons2svgfont({
  fontName: 'sheikah',
  descent: 200
});

const inputSettings = [
  {
    svgDirectory: '../output/w110_n180/round',
    charMetadata: [
      { name: '0', unicode: ['\u0030'], svgPath: '0.svg' },
      { name: '1', unicode: ['\u0031'], svgPath: '1.svg' },
      { name: '2', unicode: ['\u0032'], svgPath: '2.svg' },
      { name: '3', unicode: ['\u0033'], svgPath: '3.svg' },
      { name: '4', unicode: ['\u0034'], svgPath: '4.svg' },
      { name: '5', unicode: ['\u0035'], svgPath: '5.svg' },
      { name: '6', unicode: ['\u0036'], svgPath: '6.svg' },
      { name: '7', unicode: ['\u0037'], svgPath: '7.svg' },
      { name: '8', unicode: ['\u0038'], svgPath: '8.svg' },
      { name: '9', unicode: ['\u0039'], svgPath: '9.svg' }
    ]
  },
  {
    svgDirectory: '../output/w150_n100/rounded-bevel',
    charMetadata: [
      { name: 'A', unicode: ['\u0041'], svgPath: 'a.svg' },
      { name: 'B', unicode: ['\u0042'], svgPath: 'b.svg' },
      { name: 'C', unicode: ['\u0043'], svgPath: 'c.svg' },
      { name: 'D', unicode: ['\u0044'], svgPath: 'd.svg' },
      { name: 'E', unicode: ['\u0045'], svgPath: 'e.svg' },
      { name: 'F', unicode: ['\u0046'], svgPath: 'f.svg' },
      { name: 'G', unicode: ['\u0047'], svgPath: 'g.svg' },
      { name: 'H', unicode: ['\u0048'], svgPath: 'h.svg' },
      { name: 'I', unicode: ['\u0049'], svgPath: 'i.svg' },
      { name: 'J', unicode: ['\u004A'], svgPath: 'j.svg' },
      { name: 'K', unicode: ['\u004B'], svgPath: 'k.svg' },
      { name: 'L', unicode: ['\u004C'], svgPath: 'l.svg' },
      { name: 'M', unicode: ['\u004D'], svgPath: 'm.svg' },
      { name: 'N', unicode: ['\u004E'], svgPath: 'n.svg' },
      { name: 'O', unicode: ['\u004F'], svgPath: 'o.svg' },
      { name: 'P', unicode: ['\u0050'], svgPath: 'p.svg' },
      { name: 'Q', unicode: ['\u0051'], svgPath: 'q.svg' },
      { name: 'R', unicode: ['\u0052'], svgPath: 'r.svg' },
      { name: 'S', unicode: ['\u0053'], svgPath: 's.svg' },
      { name: 'T', unicode: ['\u0054'], svgPath: 't.svg' },
      { name: 'U', unicode: ['\u0055'], svgPath: 'u.svg' },
      { name: 'V', unicode: ['\u0056'], svgPath: 'v.svg' },
      { name: 'W', unicode: ['\u0057'], svgPath: 'w.svg' },
      { name: 'X', unicode: ['\u0058'], svgPath: 'x.svg' },
      { name: 'Y', unicode: ['\u0059'], svgPath: 'y.svg' },
      { name: 'Z', unicode: ['\u005A'], svgPath: 'z.svg' }
    ]
  },
  {
    svgDirectory: '../output/w180_n45/round',
    charMetadata: [
      { name: ' ', unicode: ['\u0020'], svgPath: 'SPACE.svg' },
      { name: '.', unicode: ['\u002E'], svgPath: 'FULL_STOP.svg' },
      { name: '-', unicode: ['\u002D'], svgPath: '-.svg' },
      { name: 'a', unicode: ['\u0061'], svgPath: 'a.svg' },
      { name: 'b', unicode: ['\u0062'], svgPath: 'b.svg' },
      { name: 'c', unicode: ['\u0063'], svgPath: 'c.svg' },
      { name: 'd', unicode: ['\u0064'], svgPath: 'd.svg' },
      { name: 'e', unicode: ['\u0065'], svgPath: 'e.svg' },
      { name: 'f', unicode: ['\u0066'], svgPath: 'f.svg' },
      { name: 'g', unicode: ['\u0067'], svgPath: 'g.svg' },
      { name: 'h', unicode: ['\u0068'], svgPath: 'h.svg' },
      { name: 'i', unicode: ['\u0069'], svgPath: 'i.svg' },
      { name: 'j', unicode: ['\u006A'], svgPath: 'j.svg' },
      { name: 'k', unicode: ['\u006B'], svgPath: 'k.svg' },
      { name: 'l', unicode: ['\u006C'], svgPath: 'l.svg' },
      { name: 'm', unicode: ['\u006D'], svgPath: 'm.svg' },
      { name: 'n', unicode: ['\u006E'], svgPath: 'n.svg' },
      { name: 'o', unicode: ['\u006F'], svgPath: 'o.svg' },
      { name: 'p', unicode: ['\u0070'], svgPath: 'p.svg' },
      { name: 'q', unicode: ['\u0071'], svgPath: 'q.svg' },
      { name: 'r', unicode: ['\u0072'], svgPath: 'r.svg' },
      { name: 's', unicode: ['\u0073'], svgPath: 's.svg' },
      { name: 't', unicode: ['\u0074'], svgPath: 't.svg' },
      { name: 'u', unicode: ['\u0075'], svgPath: 'u.svg' },
      { name: 'v', unicode: ['\u0076'], svgPath: 'v.svg' },
      { name: 'w', unicode: ['\u0077'], svgPath: 'w.svg' },
      { name: 'x', unicode: ['\u0078'], svgPath: 'x.svg' },
      { name: 'y', unicode: ['\u0079'], svgPath: 'y.svg' },
      { name: 'z', unicode: ['\u007A'], svgPath: 'z.svg' }
    ]
  }
];

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
const loadInputSetting = (inputSetting) => {
  const svgDirectory = inputSetting.svgDirectory;

  inputSetting.charMetadata.forEach((metadata) => {
    const svgPath = path.join(svgDirectory, metadata.svgPath);
    const glyph = fs.createReadStream(svgPath);
    glyph.metadata = {
      name: metadata.name,
      unicode: metadata.unicode
    };
    fontStream.write(glyph);
  });
};

inputSettings.forEach(loadInputSetting);

// Do not forget to end the stream
fontStream.end();
