import asyncio
from azurenative import ResourceBuilder, BuildContext
from config import Config

def read_yaml_file():
    with open("config.yaml") as config_yaml_file:
        return config_yaml_file.read()

async def main():

    read_yaml : str = read_yaml_file()
    parsed_yaml : Config = Config.from_yaml(read_yaml)

    #pprint.pprint(parsed_yaml)

    # Iterate through the teams, services, and environments in the YAML configuration
    # Each environment will contain configurations for different modules in the Pulumi Registry
    for team in parsed_yaml.teams:
        for service in team.services:
            for environment in service.environments:

                # AzureNative
                context = BuildContext(team.name, service.name, environment.name, environment.location, environment.tags or {})
                builder = ResourceBuilder(context)
                await builder.build(environment.azure_native)

if __name__ == "__main__":
    asyncio.ensure_future(main())
