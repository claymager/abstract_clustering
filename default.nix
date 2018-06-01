with import <nixpkgs> {};
let dsPythonPackages = pythonPackages: with pythonPackages; [
  pandas
  bokeh
  gensim
  flask
  selenium
  scikitlearn
  nltk
  pip
  jupyter
  seaborn
  pymongo
];
in stdenv.mkDerivation rec {
  name = "env";
  env = buildEnv {name = name; paths = buildInputs; };
  buildInputs = [
    (python3.withPackages dsPythonPackages)
  ];
  shellHook = "fish";
}

