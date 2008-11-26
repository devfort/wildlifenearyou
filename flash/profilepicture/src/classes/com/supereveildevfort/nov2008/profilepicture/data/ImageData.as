﻿package com.supereveildevfort.nov2008.profilepicture.data {	import flash.display.Bitmap;			import com.supereveildevfort.nov2008.profilepicture.model.FacePart;		import com.supereveildevfort.nov2008.profilepicture.model.FaceArea;		import com.supereveildevfort.nov2008.profilepicture.model.FaceAreaCategory;		import com.supereveildevfort.nov2008.profilepicture.model.ProfileImages;			import flash.events.Event;			import br.com.stimuli.loading.BulkErrorEvent;		import br.com.stimuli.loading.BulkProgressEvent;		import br.com.stimuli.loading.BulkLoader;				import flash.events.EventDispatcher; 		/**	 * @class ImageData.as	 * @namespace com.supereveildevfort.nov2008.profilepicture.data	 * @author Niqui Merret	 * @version 1.0	 * @date Nov 24, 2008	 * @description	 * @usage	 * NOTE:	 * TODO:	 *	 */	public class ImageData extends EventDispatcher 	{				private static var mInstance : ImageData;		private static var allowInst : Boolean;		private var mBulkLoader : BulkLoader;		private var mProfileImages : ProfileImages;		/**		 *********************************************************************************************************************************************************		 * 		 * public		 * 		 *********************************************************************************************************************************************************		 */				public function parseXML (pXML : XML) : void		{			//set up loader for images			mBulkLoader = new BulkLoader("images");                        //parse XML			parseProfileImages(pXML);            			//start load of images			loadImages();					}				/**		 *********************************************************************************************************************************************************		 * 		 * getters and setters		 * 		 *********************************************************************************************************************************************************		 */				public function get profileImages () : ProfileImages		{			return mProfileImages;		}				/**		 *********************************************************************************************************************************************************		 * 		 * private		 * 		 *********************************************************************************************************************************************************		 */						private function parseProfileImages (pXML : XML) : void		{						mProfileImages = new ProfileImages();						var items:XMLList = pXML.faceareacategory;			var len:int = items.length();			var i:int;						var faceAreaCatList : Array = new Array();			var faceAreaCat : FaceAreaCategory;				for (i = 0; i < len; i++)			{				faceAreaCat = new FaceAreaCategory();				faceAreaCat.name = items[i].@name;				faceAreaCat.faceareas = parseFaceAreas(items[i].facearea);								faceAreaCatList.push(faceAreaCat);							}						mProfileImages.faceareacategories = faceAreaCatList;					}		private function parseFaceAreas (pXML : XMLList) : Array		{						var items:XMLList = pXML;			var len:int = items.length();			var i:int;						var faceAreaList : Array = new Array();			var faceArea : FaceArea;				for (i = 0; i < len; i++)			{				faceArea = new FaceArea();				faceArea.name = items[i].@name;				faceArea.faceparts = parseFacePart(items[i].facepart);				faceAreaList.push(faceArea);							}			return faceAreaList;		}						private function parseFacePart (pXML : XMLList) : Array		{						var items:XMLList = pXML;			var len:int = items.length();			var i:int;						var facePartList : Array = new Array();			var facePart : FacePart;				for (i = 0; i < len; i++)			{							facePart = new FacePart();				facePart.id = i;				facePart.uid = items[i].@id;				facePart.src = items[i].@src;				facePart.title = items[i].@title;				facePartList.push(facePart);				mBulkLoader.add(facePart.src);							}						return facePartList;					}						//NOTE: not sure if this is the best way... need to rethink this!		private function loadImages () : void		{			trace("loadImages");			mBulkLoader.addEventListener(BulkProgressEvent.COMPLETE, onAllItemsLoaded);        	mBulkLoader.addEventListener(BulkErrorEvent.ERROR, onLoadError);    		mBulkLoader.start();    				}		/**		 *********************************************************************************************************************************************************		 * 		 * events		 * 		 *********************************************************************************************************************************************************		 */		 			private function onAllItemsLoaded (e : BulkProgressEvent) : void		{				for (var i : Number = 0; i < mProfileImages.faceareacategories.length; i++) 			{								for (var j : Number = 0; j < mProfileImages.faceareacategories[i].faceareas.length; j++) 				{										for (var k : Number = 0; k < mProfileImages.faceareacategories[i].faceareas[j].faceparts.length; k++) 					{						mProfileImages.faceareacategories[i].faceareas[j].faceparts[k].image = Bitmap(mBulkLoader.getContent(mProfileImages.faceareacategories[i].faceareas[j].faceparts[k].src));					}									}											}						dispatchEvent(new Event(Event.COMPLETE));		}		private function onLoadError (e : BulkErrorEvent) : void		{			trace("error loading images");		}				/**		 *********************************************************************************************************************************************************		 * 		 * singleton hack		 * 		 *********************************************************************************************************************************************************		 */		 		 		public function ImageData()		{			if (!allowInst) {	            throw new Error("Error: Instantiation failed: Use ImageData.getInstance() instead of new.");	          }		}					public static function getInstance() : ImageData		{						if (mInstance == null)			{            	allowInst = true;				mInstance = new ImageData();				allowInst = false;				}						return mInstance;					}					}}