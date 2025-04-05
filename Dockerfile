FROM nixos/nix
# RUN nix-channel --update
RUN nix-env -iA tinycc -f https://github.com/NixOS/nixpkgs/archive/21808d22b1cda1898b71cf1a1beb524a97add2c4.tar.gz
# RUN nix-build -A tinycc '<nixpkgs>'
COPY pix.py pix.py
COPY test.c test.c
RUN /nix/store/zv1kaq7f1q20x62kbjv6pfjygw5jmwl6-python3-3.12.7/bin/python3 pix.py
CMD ["/nix/store/nqh2i4ia9dk2wbs8hv7fvdy3xx2f2n42-simple/bin/hello"]
