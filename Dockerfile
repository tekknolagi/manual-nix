FROM nixos/nix
RUN nix-channel --update
RUN nix-build -A tinycc '<nixpkgs>'
COPY pix.py pix.py
COPY test.c test.c
RUN /nix/store/zv1kaq7f1q20x62kbjv6pfjygw5jmwl6-python3-3.12.7/bin/python3 pix.py
CMD ["/nix/store/jw7s07x9fi826v9cyasz0qhc1xy1mjgk-simple/bin/hello"]
