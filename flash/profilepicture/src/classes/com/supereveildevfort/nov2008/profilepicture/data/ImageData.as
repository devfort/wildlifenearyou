﻿package com.supereveildevfort.nov2008.profilepicture.data {	import flash.events.Event;		import flash.display.Bitmap;			import br.com.stimuli.loading.BulkErrorEvent;		import br.com.stimuli.loading.BulkProgressEvent;		import br.com.stimuli.loading.BulkLoader;			import com.supereveildevfort.nov2008.profilepicture.model.FacialElement;		import com.supereveildevfort.nov2008.profilepicture.model.FacialElements;			import flash.events.EventDispatcher; 		/**	 * @class ImageData.as	 * @namespace com.supereveildevfort.nov2008.profilepicture.data	 * @author Niqui Merret	 * @version 1.0	 * @date Nov 24, 2008	 * @description	 * @usage	 * NOTE:	 * TODO:	 *	 */	public class ImageData extends EventDispatcher 	{				private static var mInstance : ImageData;		private static var allowInst : Boolean;		private var mFaces : FacialElements;		private var mMouths : FacialElements;		private var mFacialHair : FacialElements;		private var mNoses : FacialElements;		private var mCheeks : FacialElements;		private var mEyes : FacialElements;		private var mEars : FacialElements;		private var mHair : FacialElements;		private var mHairAccessories : FacialElements;		private var mBulkLoader : BulkLoader;		/**		 *********************************************************************************************************************************************************		 * 		 * public		 * 		 *********************************************************************************************************************************************************		 */				public function parseXML (pXML : XML) : void		{			//set up loader for images			mBulkLoader = new BulkLoader("images");                        //parse XML			mFaces = parseFaces(pXML, "faces", "face");			mMouths = parseFaces(pXML, "mouths", "mouth");			mFacialHair = parseFaces(pXML, "facial-hairs", "facial-hair");			mNoses = parseFaces(pXML, "noses", "nose");			mCheeks = parseFaces(pXML, "cheeks", "cheek");			mEyes = parseFaces(pXML, "eyes", "eye");			mEars = parseFaces(pXML, "ears", "ear");			mHair = parseFaces(pXML, "hairs", "hair");			mHairAccessories = parseFaces(pXML, "hair-accessories", "hair-accessory");						//start load of images			loadImages();					}				/**		 *********************************************************************************************************************************************************		 * 		 * getters and setters		 * 		 *********************************************************************************************************************************************************		 */				public function get faces () : FacialElements		{			return mFaces;		}				public function get mouths () : FacialElements		{			return mMouths;		}				public function get facialHair () : FacialElements		{			return mFacialHair;		}				public function get noses () : FacialElements		{			return mNoses;		}				public function get cheeks () : FacialElements		{			return mCheeks;		}				public function get eyes () : FacialElements		{			return mEyes;		}				public function get ears () : FacialElements		{			return mEars;		}					public function get hair () : FacialElements		{			return mHair;		}				public function get hairAccessories () : FacialElements		{			return mHairAccessories;		}				/**		 *********************************************************************************************************************************************************		 * 		 * private		 * 		 *********************************************************************************************************************************************************		 */						private function parseFaces (pXML : XML, pElement : String, pElements : String) : FacialElements		{									var items:XMLList = pXML[pElement][pElements];			var len:int = items.length();			var i:int;						var faceList : Array = new Array();			var face : FacialElement;				for (i = 0; i < len; i++)			{				face = new FacialElement();				face.id = i;				face.uid = items[i].@id;				face.title = items[i].@title;				face.src = items[i].@src;				faceList.push(face);								//add to load queue				mBulkLoader.add(face.src);			}						var faces = new FacialElements();			faces.title = pXML.faces.@name;			faces.description = pXML.faces.@description;			faces.elements = faceList;						return faces;					}				//NOTE: not sure if this is the best way... need to rethink this!		private function loadImages () : void		{			trace("loadImages");			mBulkLoader.addEventListener(BulkProgressEvent.COMPLETE, onAllItemsLoaded);        	mBulkLoader.addEventListener(BulkErrorEvent.ERROR, onLoadError);    		mBulkLoader.start();    				}		/**		 *********************************************************************************************************************************************************		 * 		 * events		 * 		 *********************************************************************************************************************************************************		 */		 			private function onAllItemsLoaded (e : BulkProgressEvent) : void		{			var len:int;			var i:int;						len = mFaces.elements.length;			for (i = 0; i < len; i++)			{				mFaces.elements[i].image = Bitmap(mBulkLoader.getContent(mFaces.elements[i].src));			}						len = mMouths.elements.length;			for (i = 0; i < len; i++)			{				mMouths.elements[i].image = Bitmap(mBulkLoader.getContent(mMouths.elements[i].src));			}						len = mFacialHair.elements.length;			for (i = 0; i < len; i++)			{				mFacialHair.elements[i].image = Bitmap(mBulkLoader.getContent(mFacialHair.elements[i].src));			}						len = mNoses.elements.length;			for (i = 0; i < len; i++)			{				mNoses.elements[i].image = Bitmap(mBulkLoader.getContent(mNoses.elements[i].src));			}						len = mCheeks.elements.length;			for (i = 0; i < len; i++)			{				mCheeks.elements[i].image = Bitmap(mBulkLoader.getContent(mCheeks.elements[i].src));			}						len = mEyes.elements.length;			for (i = 0; i < len; i++)			{				mEyes.elements[i].image = Bitmap(mBulkLoader.getContent(mEyes.elements[i].src));			}						len = mEars.elements.length;			for (i = 0; i < len; i++)			{				mEars.elements[i].image = Bitmap(mBulkLoader.getContent(mEars.elements[i].src));			}						len = mHair.elements.length;			for (i = 0; i < len; i++)			{				mHair.elements[i].image = Bitmap(mBulkLoader.getContent(mHair.elements[i].src));			}						len = mHairAccessories.elements.length;			for (i = 0; i < len; i++)			{				mHairAccessories.elements[i].image = Bitmap(mBulkLoader.getContent(mHairAccessories.elements[i].src));			}						dispatchEvent(new Event(Event.COMPLETE));		}		private function onLoadError (e : BulkErrorEvent) : void		{			trace("error loading images");		}				/**		 *********************************************************************************************************************************************************		 * 		 * singleton hack		 * 		 *********************************************************************************************************************************************************		 */		 		 		public function ImageData()		{			if (!allowInst) {	            throw new Error("Error: Instantiation failed: Use ImageData.getInstance() instead of new.");	          }		}					public static function getInstance() : ImageData		{						if (mInstance == null)			{            	allowInst = true;				mInstance = new ImageData();				allowInst = false;				}						return mInstance;					}					}}