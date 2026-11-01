import asyncio
from app.services.ollama_extractor import extract_client_brief_local


async def main():

    message = """
    I own a furniture company called Oak & Home.

    I need an ecommerce website with a product catalog,
    shopping cart and online payments.

    My budget is PHP 120,000.
    I want to launch by December 1, 2026.
    """

    result = await extract_client_brief_local(message)

    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())