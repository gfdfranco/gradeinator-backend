import click
from flask.cli import with_appcontext
from app import db


@click.command()
@with_appcontext
def init_db():
    """Initialize the database."""
    db.create_all()
    click.echo('Initialized the database.')


@click.command()
@with_appcontext
def reset_db():
    """Reset the database."""
    db.drop_all()
    db.create_all()
    click.echo('Reset the database.')


def init_app(app):
    """Register CLI commands with the Flask app."""
    app.cli.add_command(init_db)
    app.cli.add_command(reset_db)
