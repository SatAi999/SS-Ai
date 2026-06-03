import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import { Camera, Upload, X, ImageIcon, Loader2 } from 'lucide-react'
import imageCompression from 'browser-image-compression'
import useAppStore from '../../store/useAppStore'
import { useTranslation } from '../../i18n/translations'

const ACCEPTED_TYPES = { 'image/*': ['.jpg', '.jpeg', '.png', '.webp', '.gif'] }
const MAX_SIZE_MB = 10

const ImageUpload = ({ compact = false }) => {
  const { language, setUploadedImage, uploadedImage, imagePreview, clearImage } = useAppStore()
  const { t } = useTranslation(language)
  const [compressing, setCompressing] = useState(false)
  const [error, setError] = useState(null)

  const processFile = useCallback(
    async (file) => {
      setError(null)
      if (file.size > MAX_SIZE_MB * 1024 * 1024) {
        setError(language === 'hi' ? 'फ़ाइल बहुत बड़ी है। 10MB से कम होनी चाहिए।' : 'File too large. Max 10MB.')
        return
      }
      setCompressing(true)
      try {
        const preview = URL.createObjectURL(file)
        let compressed = file
        if (file.size > 800 * 1024) {
          compressed = await imageCompression(file, {
            maxSizeMB: 0.8,
            maxWidthOrHeight: 1024,
            useWebWorker: true,
          })
        }
        setUploadedImage(compressed, preview)
      } catch {
        setError(language === 'hi' ? 'चित्र संसाधित नहीं हो सका।' : 'Could not process image.')
      } finally {
        setCompressing(false)
      }
    },
    [language, setUploadedImage],
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: ACCEPTED_TYPES,
    maxFiles: 1,
    noClick: !!uploadedImage,
    onDrop: ([file]) => file && processFile(file),
    onDropRejected: () =>
      setError(language === 'hi' ? 'केवल छवि फ़ाइलें स्वीकार्य हैं।' : 'Only image files accepted.'),
  })

  // Compact mode: just an icon button
  if (compact && !uploadedImage) {
    return (
      <label className="touch-target cursor-pointer rounded-xl text-slate-500 hover:text-primary-600 hover:bg-primary-50 transition-colors flex items-center justify-center">
        <input
          type="file"
          accept="image/*"
          capture="environment"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && processFile(e.target.files[0])}
        />
        {compressing ? (
          <Loader2 className="w-5 h-5 animate-spin" />
        ) : (
          <Camera className="w-5 h-5" />
        )}
      </label>
    )
  }

  return (
    <div className="w-full">
      <AnimatePresence mode="wait">
        {uploadedImage ? (
          <motion.div
            key="preview"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="relative rounded-2xl overflow-hidden border-2 border-primary-200 bg-primary-50"
          >
            <img
              src={imagePreview}
              alt="Upload preview"
              className="w-full max-h-48 object-contain"
            />
            <div className="absolute top-2 right-2 flex gap-2">
              <button
                onClick={clearImage}
                aria-label={t.imageRemovedLabel}
                className="w-7 h-7 rounded-full bg-red-500 text-white flex items-center justify-center shadow-md hover:bg-red-600 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="px-3 py-2 bg-primary-100/80 text-xs text-primary-800 font-medium flex items-center gap-1.5">
              <ImageIcon className="w-3.5 h-3.5" />
              {t.analyzeImageLabel}
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="dropzone"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all duration-200
              ${isDragActive
                ? 'border-primary-400 bg-primary-50 scale-[1.02]'
                : 'border-slate-200 bg-slate-50 hover:border-primary-300 hover:bg-primary-50'
              }
            `}
          >
            <input {...getInputProps()} />
            <div className="flex flex-col items-center gap-3">
              {compressing ? (
                <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
              ) : (
                <div className="w-12 h-12 rounded-2xl bg-primary-100 flex items-center justify-center">
                  <Upload className="w-6 h-6 text-primary-600" />
                </div>
              )}
              <div>
                <p className="text-sm font-semibold text-slate-700">
                  {isDragActive
                    ? (language === 'hi' ? 'यहाँ छोड़ें' : 'Drop here')
                    : t.uploadImage}
                </p>
                <p className="text-xs text-slate-400 mt-1">
                  {language === 'hi'
                    ? 'JPG, PNG, WebP — 10MB तक'
                    : 'JPG, PNG, WebP — up to 10MB'}
                </p>
              </div>
              {/* Camera button for mobile */}
              <label className="mt-1 inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-xl cursor-pointer hover:bg-primary-700 transition-colors">
                <Camera className="w-4 h-4" />
                {language === 'hi' ? 'कैमरा' : 'Camera'}
                <input
                  type="file"
                  accept="image/*"
                  capture="environment"
                  className="hidden"
                  onChange={(e) => e.target.files?.[0] && processFile(e.target.files[0])}
                />
              </label>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {error && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-2 text-xs text-red-600"
        >
          {error}
        </motion.p>
      )}
    </div>
  )
}

export default ImageUpload
