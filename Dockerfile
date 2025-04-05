FROM nixos/nix

RUN nix-channel --update

# RUN nix-build -A pythonFull '<nixpkgs>'

# COPY simple.json simple.json
COPY pix.py pix.py
RUN /nix/store/zv1kaq7f1q20x62kbjv6pfjygw5jmwl6-python3-3.12.7/bin/python3 pix.py
# RUN nix --extra-experimental-features nix-command derivation add < simple.json
# RUN nix-store --realize /nix/store/vh5zww1mqbcshfcblrw3y92v7kkzamfx-simple.drv
# RUN sha256sum /nix/store/vzd0wy5w6g7b52plkyckrnxdfpkg15rh-simple.drv
# RUN cat /nix/store/vzd0wy5w6g7b52plkyckrnxdfpkg15rh-simple.drv
# RUN nix-store --query --outputs /nix/store/vzd0wy5w6g7b52plkyckrnxdfpkg15rh-simple.drv
# RUN sh test.sh
# RUN nix-hash --type sha256 --truncate --base32 /nix/store/vzd0wy5w6g7b52plkyckrnxdfpkg15rh-simple.drv
# RUN echo /nix/store/$(nix-store --query --outputs $(nix --extra-experimental-features nix-command derivation add < simple.json))-simple.drv
# RUN nix derivation --extra-experimental-features nix-command show /nix/store/vzd0wy5w6g7b52plkyckrnxdfpkg15rh-simple.drv
# RUN nix --extra-experimental-features nix-command path-info --derivation /nix/store/vzd0wy5w6g7b52plkyckrnxdfpkg15rh-simple.drv
# RUN nix-store --realize /nix/store/vh5zww1mqbcshfcblrw3y92v7kkzamfx-simple.drv
# CMD cat /nix/store/5bkcqwq3qb6dxshcj44hr1jrf8k7qhxb-simple
