import asyncio
import aiohttp
import datetime
from models import engine, Session, Base, SwapiPeople

async def get_people(session, people_id):
    print(f'{people_id=} started')
    async with session.get(f'https://swapi.dev/api/people/{people_id}') as response:
        json_data = await response.json()
        if "detail" in json_data:
            return {}
        print(f'{people_id=} finished')
        return json_data

async def follow_url(session, url):
    print(f'{url=} started')
    async with session.get(f'{url}') as response:
        json_data = await response.json()
        print(f'{url=} finished')
        return json_data

async def paste_to_db(results):
    swapi_people = [SwapiPeople(name=item['name'], birth_year=item['birth_year'], created=datetime.datetime.fromisoformat(item['created'][:-1]), edited=datetime.datetime.fromisoformat(item['edited'][:-1]), eye_color=item['eye_color'],films=item['films'], gender=item['gender'],
                                hair_color=item['hair_color'], height=int(item['height']), homeworld=item['homeworld'], mass=int(item['mass']), skin_color=item['skin_color'], species=item['species'], starships=item['starships'],
                                vehicles=item['vehicles'], url=item['url']) for item in results if item is not None]
    async with Session() as session:
        session.add_all(swapi_people)
        await session.commit()

async def add_species(session, results):
    new_results = []
    for result in results:
        if not result:
            return
        species = result['species']
        coros_species = [follow_url(session, specie) for specie in species]
        res_species = await asyncio.gather(*coros_species)
        final_species = [item['name'] for item in res_species]
        result['species'] = list_to_str(final_species)
        new_results.append(result)
    return new_results

async def add_vehicles(session, results):
    new_results = []
    for result in results:
        if not result:
            return
        vehicles = result['vehicles']
        coros_vehicles = [follow_url(session, vehilce) for vehilce in vehicles]
        res_vehicles = await asyncio.gather(*coros_vehicles)
        final_vehicles = [item['name'] for item in res_vehicles]
        result['vehicles'] = list_to_str(final_vehicles)
        new_results.append(result)
    return new_results

async def add_films(session, results):
    new_results = []
    for result in results:
        if not result:
            return
        films = result['films']
        coros_films = [follow_url(session, film) for film in films]
        res_films = await asyncio.gather(*coros_films)
        final_films = [item['title'] for item in res_films]
        result['films'] = list_to_str(final_films)
        new_results.append(result)
    return new_results

async def add_starships(session, results):
    new_results = []
    for result in results:
        if not result:
            return
        starships = result['starships']
        coros_starships = [follow_url(session, starship) for starship in starships]
        res_starships = await asyncio.gather(*coros_starships)
        final_starships = [item['name'] for item in res_starships]
        result['starships'] = list_to_str(final_starships)
        new_results.append(result)
    return new_results

def list_to_str(list):
    return ' ,'.join(list)

async def main():
    start = datetime.datetime.now()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session = aiohttp.ClientSession()

    coros = []
    for item in range(1, 11):
        coros.append(get_people(session, item))
    results = await asyncio.gather(*coros)

    for item in results:
        print(item)

    coros_sub = []
    coros_sub.append(add_species(session, results))
    coros_sub.append(add_vehicles(session, results))
    coros_sub.append(add_films(session, results))
    coros_sub.append(add_starships(session, results))
    resulst_with_sublinks = await asyncio.gather(*coros_sub)

    asyncio.create_task(paste_to_db(resulst_with_sublinks[0]))

    await session.close()
    set_tasks = asyncio.all_tasks()
    for task in set_tasks:
        if task != asyncio.current_task():
            await task
    print(datetime.datetime.now() - start)


asyncio.run(main())