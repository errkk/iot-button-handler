1. Install serverless
```sh
yarn global add serverless
```

2. Create Venv & install deps
```sh
make create_venv
make install
```

3. Set development env variables
```sh
export arn=

# Hue
export hue_application_key=
export hue_client_id=
export hue_client_secret=
export hue_token_key=

# Sonos
export sonos_client_id=
export sonos_client_secret=
export sonos_token_key=
export sonos_household=
```
4. Run locally
```sh
make run
```
or
```sh
make watch
```

5. Deploy
```sh
make deploy
```

6. Get tokens
Each time you deploy, it overwrites the tags unfortunately, so re-auth is the easiest thing to do for now
```sh
make get_tokens
```
