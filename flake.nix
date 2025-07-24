{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  
  outputs = { self, nixpkgs }: let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
    python = (pkgs.python313.withPackages (ps: with ps; [
      requests
      pygobject3
      pygobject-stubs
    ]));

    buildInputs = with pkgs; [
      meson
      ninja
      python
      pkg-config
      blueprint-compiler
    ];

    nativeBuildInputs = with pkgs; [
      gtk4
      libadwaita
      gobject-introspection
      wrapGAppsHook
    ];
  in {
    devShells.${system}.default = pkgs.mkShell {
      inherit buildInputs nativeBuildInputs;
      packages = with pkgs; [
        ruff
      ];
    };
    packages.${system}.default = pkgs.stdenv.mkDerivation {
      name = "Banana";
      pname = "banana";
      version = "v0.1.0";
      src = ./.;

      inherit buildInputs nativeBuildInputs;
    };
  };
}
