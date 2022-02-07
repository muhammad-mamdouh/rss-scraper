from django.urls import reverse

from rss_scraper.feeds.enums import ItemStatus


class TestFeedViewSetUrls:
    def test__feed_viewset_list_and_create_api_v1_url__without_params__should_be_valid_url(
        self,
    ):
        reversed_url = reverse("api:feed-list")
        expected_url = "/api/v1/feeds/"

        assert reversed_url == expected_url

    def test__feed_viewset_retrieve_api_v1_url__with_feed_pk__should_be_valid_url(self):
        pk = 1
        reversed_url = reverse("api:feed-detail", kwargs={"pk": pk})
        expected_url = f"/api/v1/feeds/{pk}/"

        assert reversed_url == expected_url

    def test__feed_viewset_follow_api_v1_url__with_feed_pk__should_be_valid_url(self):
        pk = 1
        reversed_url = reverse("api:feed-follow", kwargs={"pk": pk})
        expected_url = f"/api/v1/feeds/{pk}/follow/"

        assert reversed_url == expected_url

    def test__feed_viewset_unfollow_api_v1_url__with_feed_pk__should_be_valid_url(self):
        pk = 1
        reversed_url = reverse("api:feed-unfollow", kwargs={"pk": pk})
        expected_url = f"/api/v1/feeds/{pk}/unfollow/"

        assert reversed_url == expected_url

    def test__feed_viewset_force_update_api_v1_url__with_feed_pk__should_be_valid_url(
        self,
    ):
        pk = 1
        reversed_url = reverse("api:feed-force-update", kwargs={"pk": pk})
        expected_url = f"/api/v1/feeds/{pk}/force-update/"

        assert reversed_url == expected_url

    def test__feed_viewset_items_api_v1_url__with_feed_pk__should_be_valid_url(self):
        pk = 1
        reversed_url = reverse("api:feed-items", kwargs={"pk": pk})
        expected_url = f"/api/v1/feeds/{pk}/items/"

        assert reversed_url == expected_url


class TestItemViewSetUrls:
    def test__item_viewset_list_api_v1_url__without_params__should_be_valid_url(
        self,
    ):
        reversed_url = reverse("api:item-list")
        expected_url = "/api/v1/items/"

        assert reversed_url == expected_url

    def test__item_viewset_retrieve_api_v1_url__with_item_pk__should_be_valid_url(self):
        pk = 1
        reversed_url = reverse("api:item-detail", kwargs={"pk": pk})
        expected_url = f"/api/v1/items/{pk}/"

        assert reversed_url == expected_url

    def test__item_viewset_mark_as_read_api_v1_url__with_item_pk__should_be_valid_url(
        self,
    ):
        pk = 1
        reversed_url = reverse("api:item-mark-as-read", kwargs={"pk": pk})
        expected_url = f"/api/v1/items/{pk}/mark-as-read/"

        assert reversed_url == expected_url

    def test__item_viewset_items_api_v1_url__with_filter_based_on_status_globally__should_be_valid_url(
        self,
    ):
        reversed_url = reverse("api:item-list")
        reversed_url += f"?status={ItemStatus.READ.value}"
        expected_url = f"/api/v1/items/?status={ItemStatus.READ.value}"

        assert reversed_url == expected_url

    def test__item_viewset_items_api_v1_url__with_filter_based_on_status_per_feed__should_be_valid_url(
        self,
    ):
        feed_id = 1

        reversed_url = reverse("api:item-list")
        reversed_url += f"?status={ItemStatus.READ.value}&feed={feed_id}"
        expected_url = f"/api/v1/items/?status={ItemStatus.READ.value}&feed={feed_id}"

        assert reversed_url == expected_url
