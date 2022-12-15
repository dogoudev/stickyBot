import React, { useState, useCallback } from "react";
// http://neptunian.github.io/react-photo-gallery/
import Gallery from "react-photo-gallery";
import Carousel, { Modal, ModalGateway } from "react-images";
import axios from "axios";
import useInfiniteScroll from "react-infinite-scroll-hook";
import Measure from "react-measure";
import { photos as samplePhotos } from "./photos";
import "./Album.css";

export default function Album() {
  const [photos, setPhotos] = useState(samplePhotos);
  const [currentImage, setCurrentImage] = useState(0);
  const [viewerIsOpen, setViewerIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [pageIdx, setPageIdx] = useState(0);
  const [hasNextPage, setHasNextPage] = useState(true);

  const openLightbox = useCallback((event, { photo, index }) => {
    setCurrentImage(index);
    setViewerIsOpen(true);
  }, []);

  const closeLightbox = () => {
    setCurrentImage(0);
    setViewerIsOpen(false);
  };

  // https://coolhead.in/create-infinite-scroll-in-react
  const fetchMorePhoto = async () => {
    setLoading(true);
    setPageIdx(pageIdx + 1);
    try {
      // https://medium.com/bb-tutorials-and-thoughts/react-how-to-proxy-to-backend-server-5588a9e0347
      // TODO: remove proxy
      const response = await axios.get("/api/v1/album", {
        params: { startindex: pageIdx },
      });
      const photos = response.data.photos;
      if (photos.length > 0) {
        const newImages = photos.map((obj) => ({
          src: obj.imageUrl,
          width: 1,
          height: 1,
        }));
        //console.log(newImages);
        return setPhotos((oldImages) => [...oldImages, ...newImages]);
      }
      return setHasNextPage(false);
    } catch (e) {
      console.error(e);
      return setHasNextPage(false);
    } finally {
      return setLoading(false);
    }
  };

  const [sentryRef] = useInfiniteScroll({
    loading,
    hasNextPage,
    delayInMs: 500,
    onLoadMore: fetchMorePhoto,
  });

  return (
    <>
      <Gallery
        style={{ backgroundColor: "black" }}
        photos={photos}
        direction={"column"}
        onClick={openLightbox}
        margin={12}
        columns={(containerWidth) => {
          if (containerWidth >= 1300) {
            return 3;
          }
          return undefined;
        }}
      />
      {(loading || hasNextPage) && (
        <div ref={sentryRef} className="loading-element">
          <h1>Loading...</h1>
        </div>
      )}
      <ModalGateway>
        {viewerIsOpen ? (
          <Modal onClose={closeLightbox}>
            <Carousel
              currentIndex={currentImage}
              views={photos.map((x) => ({
                ...x,
                srcset: x.srcSet,
                caption: x.title,
              }))}
            />
          </Modal>
        ) : null}
      </ModalGateway>
    </>
  );
}
