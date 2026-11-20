// Run a gl-transitions GLSL shader (https://github.com/gl-transitions/gl-transitions, MIT) in headless
// Chromium/WebGL. Reads two raw RGB frame sequences (same length, W x H), writes the blended sequence.
//   node render.js SHADER.glsl W H N from.rgb to.rgb out.rgb [params.json] [progress.json]
const fs = require('fs');
const { chromium } = require('playwright');

(async () => {
  const [shaderPath, W, H, N, fromPath, toPath, outPath, paramsPath, progPath] = process.argv.slice(2);
  const w = +W, h = +H, n = +N, fsz = w * h * 3;
  const glsl = fs.readFileSync(shaderPath, 'utf8');
  const params = paramsPath && paramsPath !== '-' ? JSON.parse(fs.readFileSync(paramsPath, 'utf8')) : {};
  const prog = progPath ? JSON.parse(fs.readFileSync(progPath, 'utf8')) : null;
  const A = fs.readFileSync(fromPath), B = fs.readFileSync(toPath);
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader', '--use-angle=swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage();
  await page.setContent('<canvas id=c></canvas>');
  const err = await page.evaluate(({ glsl, w, h, params }) => {
    const c = document.getElementById('c'); c.width = w; c.height = h;
    const gl = c.getContext('webgl', { preserveDrawingBuffer: true, premultipliedAlpha: false });
    if (!gl) return 'no webgl';
    const vs = 'attribute vec2 p; varying vec2 uv; void main(){ uv = p * 0.5 + 0.5; gl_Position = vec4(p, 0.0, 1.0); }';
    const fsrc = 'precision highp float; varying vec2 uv; uniform sampler2D from, to; uniform float progress, ratio;\n' +
      'vec4 getFromColor(vec2 uv){ return texture2D(from, uv); }\nvec4 getToColor(vec2 uv){ return texture2D(to, uv); }\n' +
      glsl + '\nvoid main(){ gl_FragColor = transition(uv); }';
    const sh = (t, s) => { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o);
      if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o)); return o; };
    let pr;
    try { pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, fsrc)); gl.linkProgram(pr); }
    catch (e) { return String(e); }
    gl.useProgram(pr);
    const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    // defaults from "uniform T name; // = value" comments, then overrides
    const re = /uniform\s+(\w+)\s+(\w+)\s*;\s*\/\/\s*=\s*([^\n]+)/g; let m; const uni = {};
    while ((m = re.exec(glsl))) uni[m[2]] = [m[1], m[3].trim()];
    for (const k in params) uni[k] = [uni[k] ? uni[k][0] : 'float', String(params[k])];
    for (const k in uni) {
      const [t, v] = uni[k]; const l = gl.getUniformLocation(pr, k); if (!l) continue;
      const nums = (v.match(/-?\d*\.?\d+(e-?\d+)?/g) || []).map(Number);
      if (t === 'float') gl.uniform1f(l, nums[0]); else if (t === 'int' || t === 'bool') gl.uniform1i(l, /true/.test(v) ? 1 : nums[0] | 0);
      else if (t === 'vec2') gl.uniform2f(l, ...(nums.length === 1 ? [nums[0], nums[0]] : nums.slice(0, 2)));
      else if (t === 'ivec2') gl.uniform2i(l, ...(nums.length === 1 ? [nums[0], nums[0]] : nums.slice(0, 2)));
      else if (t === 'vec3') gl.uniform3f(l, ...(nums.length === 1 ? [nums[0], nums[0], nums[0]] : nums.slice(0, 3)));
      else if (t === 'vec4') gl.uniform4f(l, ...(nums.length === 1 ? [nums[0], nums[0], nums[0], nums[0]] : nums.slice(0, 4)));
    }
    gl.uniform1f(gl.getUniformLocation(pr, 'ratio'), w / h);
    const mk = (unit, name) => { const t = gl.createTexture(); gl.activeTexture(gl.TEXTURE0 + unit); gl.bindTexture(gl.TEXTURE_2D, t);
      for (const [k, v] of [[gl.TEXTURE_MIN_FILTER, gl.LINEAR], [gl.TEXTURE_MAG_FILTER, gl.LINEAR], [gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE], [gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE]]) gl.texParameteri(gl.TEXTURE_2D, k, v);
      gl.uniform1i(gl.getUniformLocation(pr, name), unit); return t; };
    window._g = { gl, pr, w, h, tA: mk(0, 'from'), tB: mk(1, 'to'), out: new Uint8Array(w * h * 4) };
    return null;
  }, { glsl, w, h, params });
  if (err) { console.error('shader error:', err); process.exit(2); }
  const out = fs.openSync(outPath, 'w');
  for (let i = 0; i < n; i++) {
    const p = prog ? prog[i] : (n === 1 ? 0.5 : i / (n - 1));
    const a = A.subarray(i * fsz, (i + 1) * fsz).toString('base64');
    const b = B.subarray(i * fsz, (i + 1) * fsz).toString('base64');
    const res = await page.evaluate(({ a, b, p }) => {
      const { gl, pr, w, h, tA, tB, out } = window._g;
      const dec = s => { const bin = atob(s); const u = new Uint8Array(bin.length); for (let j = 0; j < bin.length; j++) u[j] = bin.charCodeAt(j); return u; };
      gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false); gl.pixelStorei(gl.UNPACK_ALIGNMENT, 1);
      gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, tA); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, w, h, 0, gl.RGB, gl.UNSIGNED_BYTE, dec(a));
      gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, tB); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, w, h, 0, gl.RGB, gl.UNSIGNED_BYTE, dec(b));
      gl.uniform1f(gl.getUniformLocation(pr, 'progress'), p);
      gl.viewport(0, 0, w, h); gl.drawArrays(gl.TRIANGLES, 0, 6);
      gl.readPixels(0, 0, w, h, gl.RGBA, gl.UNSIGNED_BYTE, out);
      // rows are uploaded top-first, so uv.y=0 is the image top; readPixels returns row 0 first as well
      const rgb = new Uint8Array(w * h * 3); for (let j = 0, k = 0; j < out.length; j += 4) { rgb[k++] = out[j]; rgb[k++] = out[j + 1]; rgb[k++] = out[j + 2]; }
      let s = ''; const CH = 0x8000; for (let j = 0; j < rgb.length; j += CH) s += String.fromCharCode.apply(null, rgb.subarray(j, j + CH));
      return btoa(s);
    }, { a, b, p });
    fs.writeSync(out, Buffer.from(res, 'base64'));
  }
  fs.closeSync(out);
  await browser.close();
})();
