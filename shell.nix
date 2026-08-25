{ pkgs ? import <nixpkgs> { } }:

let
  # Runtime libs the prebuilt manylinux wheels (cv2, mediapipe, numpy) dlopen.
  # Verified minimal set: dropping any of these breaks `import`.
  libs = with pkgs; [
    stdenv.cc.cc.lib # libstdc++ — all C++ wheels
    glib # libglib/libgthread — cv2
    libGL # libGL — cv2, mediapipe
    zlib # libz — numpy, cv2
    libxcb # cv2, mediapipe
  ];
in
pkgs.mkShell {
  packages = with pkgs; [
    python313 # interpreter (pyproject requires >=3.13)
    uv # python env/package manager

    cargo # rust build (engine/)
    rustc
    maturin # builds the pyo3 engine into the wheel
    rustfmt # dev conveniences
    clippy
    rust-analyzer

    gnumake # Makefile targets
  ] ++ libs;

  env = {
    UV_PYTHON = "${pkgs.python313}/bin/python3.13";
    UV_PYTHON_DOWNLOADS = "never"; # uv-downloaded pythons don't run on NixOS
    LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath libs;
  };

  shellHook = ''
    export RUST_SRC_PATH="${pkgs.rustPlatform.rustLibSrc}"
    echo "EyeGestures dev shell — python $(python3 --version | cut -d' ' -f2), $(cargo --version)"
  '';
}
