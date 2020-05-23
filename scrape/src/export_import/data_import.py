import json
import tarfile
from datetime import datetime, timedelta
from io import BytesIO
from timeit import default_timer as timer

from data.models import Author, Category, DataSource, Paper, PaperData, PaperHost
from django.db import transaction
from django.utils.timezone import make_aware
from PIL import Image


class DataImport:
    @staticmethod
    def import_data(filepath, log=print):
        """Imports database data from .tar.gz archive to database."""
        start = timer()

        with tarfile.open(filepath) as tar:
            with tar.extractfile("data.json") as f:
                data = json.load(f)

            # JSON dict keys are always strings, cast back to integers
            data["authors"] = {int(k): v for k, v in data["authors"].items()}
            data["datasources"] = {int(k): v for k, v in data["datasources"].items()}
            data["paperhosts"] = {int(k): v for k, v in data["paperhosts"].items()}

            datasource_mapping = {}
            datasources_created = 0
            for id, datasource in data["datasources"].items():
                db_datasource, created = DataSource.objects.get_or_create(
                    name=datasource["name"]
                )
                datasource_mapping[id] = db_datasource
                if created:
                    datasources_created += 1

            category_mapping = {}
            categories_created = 0
            for id, category in data["categories"].items():
                db_category, created = Category.objects.get_or_create(
                    name=category["name"]
                )
                category_mapping[id] = db_category
                if created:
                    categories_created += 1

            paperhost_mapping = {}
            paperhosts_created = 0
            for id, paperhost in data["paperhosts"].items():
                db_paperhost, created = PaperHost.objects.get_or_create(
                    name=paperhost["name"]
                )
                paperhost_mapping[id] = db_paperhost
                if created:
                    paperhosts_created += 1

            papers_created = 0
            authors_created = 0
            for i, paper in enumerate(data["papers"]):
                if not Paper.objects.filter(doi=paper["doi"]).exists():
                    with transaction.atomic():
                        db_paper = Paper(
                            doi=paper["doi"],
                            title=paper["title"],
                            abstract=paper["abstract"],
                            version=paper["version"],
                            covid_related=paper["covid_related"],
                            url=paper["url"],
                            pdf_url=paper["pdf_url"],
                            is_preprint=paper["is_preprint"],
                            last_scrape=make_aware(
                                datetime.strptime(
                                    paper["last_scrape"], "%Y-%m-%d %H:%M:%S"
                                )
                            )
                            if paper["last_scrape"]
                            else None,
                            published_at=paper["published_at"],
                            category=category_mapping[paper["category_id"]]
                            if paper["category_id"]
                            else None,
                            data=PaperData.objects.create(content=paper["content"])
                            if paper["content"]
                            else None,
                            host=paperhost_mapping[paper["paperhost_id"]]
                            if paper["paperhost_id"]
                            else None,
                            data_source=datasource_mapping[paper["datasource_id"]],
                        )

                        db_paper.save()

                        for author_id in paper["author_ids"]:
                            author = data["authors"][author_id]
                            db_author, created = Author.objects.get_or_create(
                                first_name=author["firstname"],
                                last_name=author["lastname"],
                                data_source=datasource_mapping[
                                    author["datasource_id"]
                                ],
                            )
                            if created:
                                db_author.split_name = author["split_name"]
                                db_author.save()
                                authors_created += 1
                            db_paper.authors.add(db_author)

                        img_path = paper["image"]
                        if img_path:
                            with tar.extractfile(img_path) as img_file:
                                image = Image.open(img_file)
                                buffer = BytesIO()
                                image.save(buffer, format="JPEG")
                                db_paper.add_preview_image(buffer)
                        db_paper.save()
                    papers_created += 1

        end = timer()

        log(f"Finished import in {timedelta(seconds=end - start)}")
        log("Imported")
        log(f"\t{datasources_created} datasources")
        log(f"\t{paperhosts_created} paperhosts")
        log(f"\t{categories_created} categories")
        log(f"\t{authors_created} authors")
        log(f"\t{papers_created} papers")
