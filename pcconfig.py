import pynecone as pc


config = pc.Config(
    app_name="gpt2_xl",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
)
