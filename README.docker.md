# local development

You'll need to have installed `docker-compose` and `docker`, and have a running
docker daemon.

# starting services with docker-compose

You should be inside the `django-gallery` directory when running this command.

```sh
docker-compose up
```

You'll see labeled output from each service.

When you make changes on your local copy of django-gallery, they will automatically propagate to the running container.

## accessing the database (cli)

There are cases where you may need access to the database (such as restoring a backup).
These commands will allow you access into the database over the command line.

1. Have docker running. Eg. `docker-compose up -f docker-compose.yaml`
2. Locate your container. `docker ps`, select the CONTAINER ID for postgres
3. Establish a shell in the container. `docker exec -t -i (CONTAINER ID) bash`
4. Connect to the database. `su postgres -c psql`

Now that you are connected to the database CLI, you can perform queries as the root postgres user.
For remote access to this database, you may create a role for yourself with the following query.
`create role your-name with superuser createdb login password 'your-password';`

To restore a database backup from the command line:
1. Find a way to copy the database into the container (or access it externally)
2. Become the postgres root user. `su postgres -c bash`
3. Stop the portal docker container (this can be accomplished with `docker stop (CONTAINER ID)`)
4. Verify that there are no other connections to the DB and enter psql
5. Rename or drop the imagehost_db database so it is out of the way
6. create the database and public schema
7. set permissions for the imagehost user
8. leave psql and run `pg_restore -F -c imagehost_dbDB.custom` on newly created imagehost_db db

Some errors are expected from the above, such as a non-existant usagereports role.
These can safely be ignored for development use (the role requires read-only access in prod)

## accessing the database (GUI)

GUI access to the database can be established with PGAdmin (3 or 4) connected to localhost.
This assumes that you created a user for yourself in the previous section
(if you haven't, you can use the imagehost user at limited permissions)

1. Open PGAdmin and add a new server with an identifying name
2. Under the connection tab
  * Hostname/address should be localhost
  * Username should be what you added in the previous section
  * Password should be what you added in the previous section
3. Save and connect, you should now be able to run queries with administrative privileges.

To restore a database backup inside PGAdmin:
1. Copy the imagehost_dbDB.custom to your desktop (or somewhere easy) and
   rename to imagehost_dbDB.backup
2. Connect to the database server
3. Stop the portal docker container (this can be accomplished with `docker stop (CONTIANER ID)`)
4. Verify that there are no other connections to the db and either rename or drop the database
5. Create a new database with the owner set to imagehost
6. Right-click the newly created database and click restore
7. Navigate to your .backup file and select that
8. Let the restore run

Some errors are expected from the above, such as a non-existant usagereports role.
These can safely be ignored for development use (the role requires read-only access in prod)

## applying migrations

After you have made changes to the database or models, migrations need
to be made and then applied. To accomplish that in the docker env:

1. Have docker running. Eg. `docker-compose up -f docker-compose.yaml`
2. Locate your container. `docker ps`, select the CONTAINER ID for the portal
3. Establish a shell in the container. `docker exec -t -i (CONTIANER ID) bash`
4. CD to the portal directory (in docker-compose.yaml, this is defined as /portal)
5. Make your migrations. `python manage.py makemigrations`
6. Apply the migrations. `python manage.py migrate`
7. Optionally exit the shell. It is no longer needed.

You may get errors on your last step if you are restoring from a database
backup. Before making the migrations, first run `python manage.py --fake-initial`

If your database has migrations applied, it should be able to continue from
whichever the last applied migration was.

# staging/testing

You'll need to have `docker-machine` installed. You can create a fully
provisioned VM on ESXi using this command:

```sh
docker-machine create \
  --driver vmwarevsphere \
  --vmwarevsphere-username root \
  --vmwarevsphere-password password \
  --vmwarevsphere-vcenter 500.500.500.500 \
  my-docker
```

You should replace `my-docker` with whatever you want to uniquely reference this
VM by.

Note: If you get an error similar to "ServerFaultCode: Current license or ESXi version prohibits execution of the requested operation."
you must first put the vmserver in "Evaluation Mode" as the Free tier license does not support remote management of VMs.
This can be accomplished by logging into the esxi interface, navigating to configuration and changing the license config.

## remote environment

First, you'll set up your local docker client to connect to the remote docker host:

```sh
eval $(docker-machine env my-docker)
```

You can see the containers running on the remote host using regular docker
commands like `docker ps`.

## create a production environment

```sh
docker-compose -f docker-compose.yaml -f docker-compose.production.yaml up
```
