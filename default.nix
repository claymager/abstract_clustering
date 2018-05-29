with import <nixpkgs> {};
let dsPythonPackages = pythonPackages: with pythonPackages; [
  pandas
  flask
  selenium
  scikitlearn
  nltk
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

