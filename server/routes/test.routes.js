const express = require("express");
const {
    createTest,
    userCreatedTests,
    testAdminData,
    testRegister,
    increasePersonDetected,
    increaseVoiceDetected,
    increaseFaceCovering,
    totalWarnings,
    terminateExam,
    allowInExam,
    getTestDetails,
    allTests,
    createdTests,
    getKeywords,
    getAttemptedTestNames,
    updateTests,
} = require("../controllers/test.control");
const { requireSignIn } = require("../middlewares");
const router = express.Router();

// user/admin can create test
router.post("/create-test", requireSignIn, createTest);

// user/admin can fetch a list of test which we created
router.get("/all-created-test", requireSignIn, userCreatedTests);

router.get("/createdTests",createdTests);

// for registering the exam
router.patch("/test-register/:test_code", requireSignIn, testRegister);

// user/admin can fetch the live status of test
router.get("/test-live-status/:test_code", requireSignIn, testAdminData);

// increasing warning count of person detected
router.patch("/warning-person-detected", requireSignIn, increasePersonDetected);

// increasing warning count of voice-detected
router.patch("/warning-voice-detected", requireSignIn, increaseVoiceDetected);

// increasing warning count of face-covering
router.patch("/warning-face-covering", requireSignIn, increaseFaceCovering);

// will give you total no of warning given to user
router.get("/total-warnings", requireSignIn, totalWarnings);

// route that will terminate the exam of candidate
router.patch("/terminate", requireSignIn, terminateExam);

// route that will allow the terminated candidates to give an exam
router.patch("/allow-in-exam", requireSignIn, allowInExam);

router.get('/test-details/:test_code', getTestDetails); 

router.get('/allTests',allTests);

router.get('/keywords',getKeywords);

router.post('/getAttemptedTestNames',getAttemptedTestNames);

router.post('/update-test',updateTests);
module.exports = router;
